#!/bin/bash
sudo apt install git -y
git clone https://opendev.org/openstack/devstack
if [ $? -ne 0 ]; then
  git clone https://github.com/openstack/devstack
  if [ $? -ne 0 ]; then
    echo "Error occurred during git clone" >&2
    exit 1
  fi
fi
cp $PWD/onehundredten/openstack/mylocal.conf $PWD/devstack/local.conf

read -r -p "Insert the password you want to assign to the openstack admin"$'\n' PASSWD ;
sed -i "s^ADMIN_PASSWORD=nomoresecret^ADMIN_PASSWORD=$PASSWD^" $PWD/devstack/local.conf
read -r -p "Insert the interface to use as FLAT_INTERFACE"$'\n' IFACE_NAME ;
sed -i "s^FLAT_INTERFACE=eth1^FLAT_INTERFACE=$IFACE_NAME^" $PWD/devstack/local.conf
IFACE_IP=$(ip addr show $IFACE_NAME | grep "inet\b" | awk '{print $2}' |  cut -d/ -f1)
sed -i "s^HOST_IP=192.168.1.111^HOST_IP=$IFACE_IP^" $PWD/devstack/local.conf
FLOAT_RANGE="192.168.1.112/28"
read -r -p "Insert the floating ip range to use on the interface $IFACE_NAME that has ip $IFACE_IP , a /27 or /28 will suffice e.g. insert 192.168.1.112/28"$'\n' FLOAT_RANGE;
sed -i "s^192.168.1.112/28^$FLOAT_RANGE^" $PWD/devstack/local.conf 

while true; do
$PWD/devstack/stack.sh
  if [ $? -eq 0 ]; then
    break
  fi
$PWD/devstack/unstack.sh
$PWD/devstack/clean.sh
done

cp $PWD/onehundredten/openstack/myprepare.sh . && sudo chmod +x myprepare.sh && ./myprepare.sh

if [ $? -eq 0 ]; then
  echo "Setup complete"
else
  echo "Error occurred during setup" >&2
  exit 1
fi