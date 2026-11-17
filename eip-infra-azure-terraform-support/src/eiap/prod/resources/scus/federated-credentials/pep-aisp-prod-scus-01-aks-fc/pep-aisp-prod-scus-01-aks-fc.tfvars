federated_credential_ids = {
  "pep-aisp-prod-scus-01-aks-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/188ef83a-9b55-4272-bed7-0c4d6aa5d302/"
    subject             = "system:serviceaccount:istio-system:pep-aisp-ingress-gw01-service-account"   
    mi_name             = "pep-aisp-nonprod-infra-kv-01-mi" 
  }
}