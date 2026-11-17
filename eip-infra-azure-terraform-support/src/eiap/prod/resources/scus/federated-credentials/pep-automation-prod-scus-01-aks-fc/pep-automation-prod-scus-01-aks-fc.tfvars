federated_credential_ids = {
  "pep-automation-prod-scus-01-aks-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/dca9bf1f-e5d2-40b3-92db-626a463c8c37/"
    subject             = "system:serviceaccount:istio-system:pep-automation-ingress-gw01-service-account"   
    mi_name             = "pep-automation-prod-infra-kv-01-mi" 
  }
}