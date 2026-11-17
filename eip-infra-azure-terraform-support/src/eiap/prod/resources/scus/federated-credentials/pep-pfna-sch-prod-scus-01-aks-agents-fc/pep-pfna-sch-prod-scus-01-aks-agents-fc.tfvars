federated_credential_ids = {
  "pep-pfna-sch-prod-scus-01-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/1a570d71-60da-4650-b7eb-7015418ad995/"
    subject             = "system:serviceaccount:pep-pfna-global-devsecops-prod:pep-pfna-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}