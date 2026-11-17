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
## 3) Create Cloud Integration Secret
#kubectl create secret generic cloud-integration -n kubecost --from-file=./manifests/cloud-integration.json &&
## 4) Azure service key - to read the billng API
#kubectl create secret generic azure-service-key -n kubecost --from-file=./manifests/service-key.json &&
## 5) Cert for the OKTA Integration
#kubectl create secret generic kubecost-okta --from-file=./manifests/myservice.cer --namespace kubecost &&
## 6) Create secret for federated store
#kubectl create secret generic federated-store -n kubecost --from-file=./manifests/federated-store.yaml &&
##-----------------------------------------------
## ********************************************
## Config map to setup RBAC
kubectl create configmap group-filters --from-file=./manifests/filters.json -n kubecost &&
## get the repo
helm repo add kubecost https://kubecost.github.io/cost-analyzer/ &&
## update the repo 
helm repo update &&
## install the helm chart with the values specific to primary cluster
helm upgrade --install kubecost kubecost/cost-analyzer --namespace kubecost -f ./manifests/values-thanos.yaml -f ./manifests/values-azure-primary.yaml -f ./manifests/values-saml.yaml --version=1.108.1

## upgrade to v2

helm upgrade --install kubecostv2 kubecost/cost-analyzer -n kubecostv2 -f values-saml.yaml -f values-azure-primary-v2.yaml --version=2.3.5