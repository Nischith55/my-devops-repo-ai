#!/bin/bash
for n in $(kubectl get ns -l istio.io/rev -o name); do 
  n=${n##namespace/}
  echo "Added label istio-injection=enabled and removed label istio.io/rev in the namespace: "$n""
  kubectl label ns "$n" istio-injection=enabled istio.io/rev-
  echo "Performing rollout restart of deployments and daemonsets in the namespace: "$n""
  kubectl rollout restart deployment -n "$n"
  kubectl rollout restart daemonset -n "$n"
  echo "Waiting for 30 seconds before moving to next namespace"
  sleep 30
done