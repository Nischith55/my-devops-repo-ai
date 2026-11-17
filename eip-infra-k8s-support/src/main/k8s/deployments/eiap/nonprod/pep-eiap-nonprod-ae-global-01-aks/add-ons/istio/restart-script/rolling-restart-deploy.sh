#!/bin/bash
for n in $(kubectl get ns -l istio-injection=enabled -o name); do 
  n=${n##namespace/}
  echo "Performing rollout restart of deployments and daemonsets in the namespace: "$n""
  kubectl rollout restart deployment -n "$n"
  kubectl rollout restart daemonset -n "$n"
  echo "Waiting for 5 seconds before moving to next namespace"
  sleep 5
done