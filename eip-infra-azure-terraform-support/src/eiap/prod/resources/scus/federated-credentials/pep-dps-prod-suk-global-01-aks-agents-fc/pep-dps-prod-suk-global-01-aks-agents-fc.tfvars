federated_credential_ids = {
  "pep-dps-prod-suk-global-01-aks-agents-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://uksouth.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/28f99192-b7e2-4050-a48e-0af95aa40e62/"
    subject             = "system:serviceaccount:pep-dps-global-devsecops-prod:pep-dps-buildagent"   
    mi_name             = "pep-aisp-prod-buildagent-01-mi" 
  }
}