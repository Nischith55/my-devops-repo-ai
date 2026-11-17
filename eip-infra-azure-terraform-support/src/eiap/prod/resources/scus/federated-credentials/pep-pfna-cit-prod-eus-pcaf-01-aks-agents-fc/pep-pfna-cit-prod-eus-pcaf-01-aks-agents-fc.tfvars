federated_credential_ids = {
  "pep-pfna-cit-prod-eus-pcaf-01-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0752a7c3-aabf-4284-b74c-68dfe3ab3a9a/"
    subject             = "system:serviceaccount:pep-pfna-global-devsecops-prod:pep-pfna-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}