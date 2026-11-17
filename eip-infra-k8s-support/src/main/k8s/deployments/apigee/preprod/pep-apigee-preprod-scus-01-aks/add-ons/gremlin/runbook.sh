#!/bin/bash
## ********************************************
## In view of security the team secret and team id are masked. These values should be procured from the SRE team
## before running the  runbook and install the tool. Ensure gremlin namespace is created before installing gremlin.
## Deploy the secret directly from local, remove reference to secret from the generated manifest file. 
##-----------------------------------------------

helm template pep-apigee-gremlin gremlin/gremlin \
--namespace pep-apigee-gremlin \
--set gremlin.hostPID=true \
--set gremlin.container.driver=containerd-runc \
--set gremlin.secret.teamID=**************************** \
--set gremlin.secret.clusterID=**************************** \
--set gremlin.secret.managed=true \
--set gremlin.secret.type=certificate \
--set-file  gremlin.secret.certificate=/PATH/TO-CERT.PEM \
--set-file  gremlin.secret.key=/PATH/TO-KEY.PEM \
--set gremlin.apparmor=unconfined \
--set       'tolerations[0].operator=Exists' > gremlin-installation.yaml
