#!/bin/bash
for n in $(kubectl get ns -l istio.io/rev=prod-stable -o name); do 
  n=${n##namespace/}
  echo "Performing rollout restart of deployments in the namespace: "$n""
  kubectl rollout restart deployment -n "$n"
  kubectl rollout restart daemonset -n "$n"
done