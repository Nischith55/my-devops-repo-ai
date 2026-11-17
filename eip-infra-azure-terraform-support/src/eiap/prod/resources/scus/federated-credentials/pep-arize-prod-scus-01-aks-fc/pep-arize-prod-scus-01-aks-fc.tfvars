federated_credential_ids = {
  "pep-arize-prod-scus-01-aks-fc" = {       
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/f8bf2703-d8c3-43ab-be86-99c264d3fbe2/"    
    subject             = "system:serviceaccount:istio-system:pep-arize-ingress-gw01-service-account"
    mi_name             = "pep-arize-prod-infra-kv-01-mi"
  }
}