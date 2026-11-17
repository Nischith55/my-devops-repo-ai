federated_credential_ids = {
  "pep-eiap-prod-suk-infra-02-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://uksouth.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/3b59b04a-58bf-4a57-a958-aa910e088eb8/"
    subject             = "system:serviceaccount:pep-eiap-global-devsecops-prod:pep-eiap-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}