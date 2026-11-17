#!/bin/bash
kubectl create namespace kubecost &&
## ********************************************
## In view of security the following manifests are not checkedin the repo and hence the 
## respective commands are commented out. But the creation of these secrets has to be taken care of 
## before installing Kubecost
##-----------------------------------------------
## 1) Create secret for product key
#kubectl create secret generic productkey -n kubecost --from-file=./manifests/productkey.json &&
## 2) Create secret for Thanos store
#kubectl create secret generic kubecost-thanos -n kubecost --from-file=./manifests/object-store.yaml &&
## 3) Create secret for federated store
#kubectl create secret generic federated-store -n kubecost --from-file=./manifests/federated-store.yaml &&
##-----------------------------------------------
## ********************************************
# get the repo
helm repo add kubecost https://kubecost.github.io/cost-analyzer/ &&
# update the repo 
helm repo update &&
# install the helm chart with the values specific to primary cluster
helm upgrade --install kubecost kubecost/cost-analyzer --namespace kubecost -f ./manifests/values-thanos.yaml -f ./manifests/values-azure-secondary-pbna-scus-prod.yaml --version=1.108.1