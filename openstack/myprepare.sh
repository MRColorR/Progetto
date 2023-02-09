NAME1='master1a' ;
NAME2='worker1a' ;
INET='0'
read -r -p "Wich is the name of the site/cloud? this will affect the nodes hostnames (eg. a , b, cloud1, cloud2, ...)"$'\n' SITE ;
read -r -p "Internal network willi be like: 172.16.x.0/24. Wich is the number x (0-255) of the site/cloud internal network? This will affect the instances internal addesses"$'\n' INET ;
read -r -p "Is this the site where the master for the k3s cluster wll be? Y/N? "$'\n' yn
        case $yn in
            [Yy]* )
                NAME1="master$INET$SITE" ;
                NAME2="worker$INET$SITE" ;;
            [Nn]* ) 
                NAME1="worker$INET$SITE" ;
                NAME2="worker$INET$SITE""1" ;;
            * ) printf "Please answer yes or no.";;
        esac 
printf "Ok, so the names and hostnames of the instances will be $NAME1 and $NAME2"$'\n';

# Use the OpenStack admin identity
source ./devstack/openrc admin admin

# Download the latest Centos 7 cloud image and add it to the OpenStack image catalog.
# The xz command is CPU intensive and will be extremely slow without nested
# virtualization. Download the non-compressed image if in doubt.

wget -O debian10.qcow2 http://cdimage.debian.org/images/cloud/OpenStack/current-10/debian-10-openstack-amd64.qcow2
openstack image create --file ./debian10.qcow2 --disk-format qcow2 --public debian10


# Create the kube project and user, and add necessary roles to the user.
#openstack project create kube
#openstack user create kube --project kube --password kube
#openstack role add --user kube --project kube member
#openstack role add --user kube --project kube load-balancer_member

# Switch to the kube user/project identity
#source ./devstack/openrc kube kube

# Create the network for the K8s cluster nodes and connect it to *public*, the external network
openstack network create kubenet
openstack subnet create --subnet-range "172.16.$INET.0/24" --network kubenet --dns-nameserver 1.1.1.1 kubesubnet
openstack router create kuberouter
openstack router set --external-gateway public kuberouter
openstack router add subnet kuberouter kubesubnet

# Create the security group for K8s cluster nodes
openstack security group create kubesg
openstack security group rule create kubesg --proto icmp


# Open network ports in *kubesg*.
# This is based on
# https://kubernetes.io/blog/2020/02/07/deploying-external-openstack-cloud-provider-with-kubeadm/
# Calico and Weave ports can probably be removed from the list below.
# ssh and http ports were added to the list.
while read proto ports description
do
    openstack security group rule create kubesg --proto $proto --dst-port $ports --description "$description"
    echo openstack security group rule create kubesg --proto $proto --dst-port $ports --description "$description"
done << EOF
TCP     22      "SSH"
TCP     80      "HTTP-for-testing"
TCP     443     "HTTPS-for-testing"
TCP     9993    "Zerotier-manage"
UDP     9993    "Zerotier-connect"
TCP     30080   "wwwProj"
TCP     30500   "apiProj"
TCP     6443    "Kubernetes-API-Server"
TCP     2379:2380       "etcd-server-client-API"
TCP     10250   "Kubelet-API"
TCP     10251   "kube-scheduler"
TCP     10252   "kube-controller-manager"
TCP     10255   "Read-only-Kubelet-API"
TCP     30000:32767     "NodePort-Services"
TCP     179     "Calico-BGP-network"
TCP     9099    "Calico-felix-(health-check)"
UDP     8285    "Flannel"
UDP     8472    "Flannel"
UDP     51820   "Wireguard"
TCP     6781:6784       "Weave-Net"
UDP     6783:6784       "Weave-Net"
EOF

# Create an SSH keypair.
# Alternatively, an existing keypair can be used.
ssh-keygen -f kubekey -P ""

# Add the public key to OpenStack
openstack keypair create --public-key kubekey.pub kubekey
sleep 1
# Launch two Centos images. They will be used to install the K8s cluster.
openstack server create --image debian10 --network kubenet --flavor d3 --key-name kubekey $NAME1
sleep 1
openstack server create --image debian10 --network kubenet --flavor d3 --key-name kubekey $NAME2
sleep 1
# Obtain two floating IPs for the cluster nodes
IP1=$(openstack floating ip create public -f value -c name)
IP2=$(openstack floating ip create public -f value -c name)
sleep 1
# Add *kubesg* and the floating IPs to the cluster nodes
openstack server add security group $NAME1 kubesg
openstack server add security group $NAME2 kubesg
openstack server add floating ip $NAME1 $IP1
openstack server add floating ip $NAME2 $IP2

NIC='eth0'
read -r -p "The default selected interface is $NIC, do you want to use a different interface? Y/N? "$'\n' yn
        case $yn in
            [Yy]* )
                read -r -p "OK, insert the name of the interface you want to use"$'\n' NIC
                printf "New interface selected is $NIC"$'\n';;
            [Nn]* ) 
                printf "Ok, the default $NIC will be used"$'\n';;
            * ) printf "Please answer yes or no.";;
        esac 

read -r -p "Do you want to enable ip_forward, proxy_arp and NAT postrouting on $NIC functions? Y/N? "$'\n' yn
        case $yn in
            [Yy]* )
                sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
                sudo sh -c "echo 1 > /proc/sys/net/ipv4/conf/$NIC/proxy_arp";;
            [Nn]* ) 
                printf "Ok, no nodifications to the VM network config";;
            * ) printf "Please answer yes or no.";;
        esac 

