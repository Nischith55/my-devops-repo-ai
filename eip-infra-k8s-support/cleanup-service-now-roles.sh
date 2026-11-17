#!/bin/bash

# Get the current context
echo "Current Context:"
kubectl config current-context

# Get the cluster roles and cluster role bindings, then filter for 'pep-eiap-service'
echo -e "\nCluster Roles and Cluster Role Bindings containing 'pep-eiap-service':"
kubectl get clusterrole,clusterrolebinding | grep pep-eiap-service

# Delete the cluster role binding 'pep-eiap-servicenow-crb'
echo -e "\nDeleting Cluster Role Binding 'pep-eiap-servicenow-crb':"
kubectl delete clusterrolebinding pep-eiap-servicenow-crb

# Delete the cluster role 'pep-eiap-servicenow-clusterrole'
echo -e "\nDeleting Cluster Role 'pep-eiap-servicenow-clusterrole':"
kubectl delete clusterrole pep-eiap-servicenow-clusterrole

# Get the service account 'pep-eiap-servicenow-sa' in the 'pep-eiap-ops-admin' namespace
echo -e "\nService Account 'pep-eiap-servicenow-sa' in namespace 'pep-eiap-ops-admin':"
kubectl get serviceaccount pep-eiap-servicenow-sa -n pep-eiap-ops-admin

# Delete the service account 'pep-eiap-servicenow-sa' in the 'pep-eiap-ops-admin' namespace
echo -e "\nDeleting Service Account 'pep-eiap-servicenow-sa' in namespace 'pep-eiap-ops-admin':"
kubectl delete sa pep-eiap-servicenow-sa -n pep-eiap-ops-admin

# Get the role binding 'pep-eiap-servicenow-rb' in the 'pep-eiap-ops-admin' namespace
echo -e "\nRole Binding 'pep-eiap-servicenow-rb' in namespace 'pep-eiap-ops-admin':"
kubectl get rolebinding pep-eiap-servicenow-rb -n pep-eiap-ops-admin

# Delete the role binding 'pep-eiap-servicenow-rb' in the 'pep-eiap-ops-admin' namespace
echo -e "\nDeleting Role Binding 'pep-eiap-servicenow-rb' in namespace 'pep-eiap-ops-admin':"
kubectl delete rolebinding pep-eiap-servicenow-rb -n pep-eiap-ops-admin
