federated_credential_ids = {
  "pep-eiap-prod-gwc-infra-02-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://germanywestcentral.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/75b70e2e-bfe8-478c-98e8-a2870d36a78f/"
    subject             = "system:serviceaccount:pep-eiap-global-devsecops-prod:pep-eiap-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}