federated_credential_ids = {
  "pep-dps-prod-scus-global-01-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/adfa3c8c-f5bf-4740-8f36-eaa63c577b8a/"
    subject             = "system:serviceaccount:pep-dps-global-devsecops-prod:pep-dps-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}