federated_credential_ids = {
  "pep-pbna-prod-eus-global-01-aks-fc" = {     
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"  
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/23b2aa85-38dc-4e11-8bad-88e664ce5b59/" 
    subject             = "system:serviceaccount:istio-system:pep-pbna-ingress-gw01-service-account"   
    mi_name             = "pep-pbna-prod-infra-kv-01-mi"         
  }
}