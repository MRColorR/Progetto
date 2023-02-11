# onehundredten

In this project we produce a working PoC of a vendor-agnostic multi-cloud bursting solution using two openstack clouds (devstack) and a multi cloud kubernetes cluster (K3s). 

The example services we run are a simple website and an API used to compute the factorial of the number entered on the website by the user. The computation is executed by the cluster and both services have their horizontal auto scaler and thanks to the labels defined on the nodes the services will be executed on the first cloud (on-prem) until no more resources are available. Then the autoscaler proceeds to burst the workload also on the second cloud (public/secondary cloud) realizing the cloud bursting function. Additionnaly in the blueprint we defined several policies for supporting auto backups/rollback of the services and rolling updates.

---

## Prerequisites
- To run the project locally you need an hypervisor and two VMs with nested virtualization capabilities and network connectivity with one or more NIC possibly with static IP adresses.
- Recomended VMs resources: 6 vCores, 12 GB RAM, 128 GB VHDD | Minimum VMs resources: 4 vCores, 8 GB RAM, 32 GB VHDD

---

## How to run
- Get the latest code from this repo
- Then setup all the components: 
  - Configure and deploy the Openstack clouds (one per VM)
    - Use the setupStackUser script to setup a user with paswordless sudo running: 
      
      ```curl https://raw.githubusercontent.com/MRColorR/onehundredten/master/openstack/setupStackUser.sh > setupStackUser.sh && sudo chmod +x setupStackUser.sh && ./setupStackUser.sh```
    - Now impersonate the stack user using: 
      
      ```sudo -u stack -i``` 
    - Run the devstack guided setup provided using: 
      
      ```sudo apt install git -y && git clone https://github.com/MRColorR/onehundredten && sudo chmod +x $PWD/onehundredten/openstack/setupAIO.sh && ./onehundredten/openstack/setupAIO.sh```
      - Notice: during these steps to make the cloud instances and cluster instances pingable on the local network you should use the same IP addresses space of your undelying network.
    - Repeat the steps on the other VM, now you have two clouds with two instances runing inside the cloud. You can check their assigned floating IPs using: 
      
      ``` source /devstack/openrc admin admin``` and then ```openstack server list```.
    - It's time to install the K3s cluter on the master node. and join the worker nodes: 
      - SSH into the master node using
        
        ```ssh -i kubekey debian@<masterNodeFloatingIP>``` 
      - Now inside the master node issue the following command: 
        
        ```sudo apt install curl -y && curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--node-external-ip <masterFloatingIP> --flannel-external-ip" sh -```
      - Retrieve from the master the cluster token that will allow us to add the worker nodes: 
        
        ```sudo cat /var/lib/rancher/k3s/server/node-token```
      - Now SSH into the workers node and make them join the cluster running the following command: 
        
        ```sudo apt install curl -y && curl -sfL https://get.k3s.io | K3S_URL=<masterFloatingIP>:6443 K3S_TOKEN="token" INSTALL_K3S_EXEC="--node-external-ip <workerFloatingIP>" sh -```
    - You can check on the master node if all is connected and running using: ```sudo kubectl get nodes``` and ```sudo kubectl top nodes```
    - To complete the project deploy the website and the factorial API using:
        
      ``` kubectl apply -f '.\k8s-www-api-blueprint.yaml' ``` 
    - You should be able to reach the website from each node on port :30080 and ask for the factorial of a number you can also contatc directly the APi on port 30500

---
### JMeter load testing
  - Jmeter here is used for load tests, see the jmeter file. After downloading jmeter latest release you can run it using: 
    
    ```.\<apache-jmeter-x.yFolder>\bin\jmeter.bat -f -n -t '.\HTTP Request www and api 2.jmx' -l .\Report_HTML\results.csv -e -o .\Report_HTML\```
