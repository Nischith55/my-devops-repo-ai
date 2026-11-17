federated_credential_ids = {
  "pep-eiap-prod-eus-infra-02-aks-fc" = {       #### SK11 --> FC-NAME (Note: it should match with folder name and fc.tfvars filename)
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"       #### SK11--> RG of MI
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/f2425711-5a81-4738-8aa6-04e423a0eddb/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"   
    mi_name             = "pep-eiap-prod-infra-kv-01-mi" 
  }
}