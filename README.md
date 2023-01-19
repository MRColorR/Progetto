# onehundredten

This is a (Rancher) K8s horizontal scaling cluster with cloud ursting capabilities that run a sample website and an API used to compute the factorial of the number entered on the site by the user. 

---

## Prerequisites

- ### A cluster 
  - It could be a Rancher K8s cluster or just regular K8s cluster

- ### K8s metric server
  - If k8s metric server is not already installed in your k8s cluster you can use the provided blueprint to install it runing:
```
kubectl apply -f '.\metric-server.yaml'   
```

## How to run
- Get the latest code from this repo. Then to deploy all the components:
  - ( For Regular K8s cluster) from the repo's folder run: ``` kubectl apply -f '.\k8s-www-api-blueprint.yaml' ```
  - (For Racher K8s cluster) open Rancher's dashboard and import the yaml file or open the kubectl console in Rancher's dashboard and use the same command written above



---
### JMeter load testing
  - Jmeter here is used for load tests, see the jmeter file. After downloading jmeter latest release you can run it using:
```
.\bin\jmeter.bat -f -n -t '.\HTTP Request site and api.jmx' -l .\Report_HTML\results.csv -e -o .\Report_HTML\
```
