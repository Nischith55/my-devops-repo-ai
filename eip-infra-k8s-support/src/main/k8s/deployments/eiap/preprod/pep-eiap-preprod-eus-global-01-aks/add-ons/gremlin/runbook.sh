#!/bin/bash
## ********************************************
## In view of security the team secret and team id are masked. These values should be procured from the SRE team
## before running the  runbook and install the tool
##-----------------------------------------------

helm template pep-eiap-gremlin gremlin/gremlin \
--namespace pep-eiap-gremlin \
--set gremlin.hostPID=true \
--set gremlin.container.driver=containerd-runc \
--set gremlin.secret.teamID=**************************** \
--set gremlin.secret.teamSecret=************************* \
--set gremlin.secret.clusterID=pep-eiap-preprod-eus-global-01-aks \
--set gremlin.secret.managed=true \
--set gremlin.secret.type=secret \
--set gremlin.installApparmorProfile=true > /manifests/gremlin-installation.yaml
