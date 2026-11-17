federated_credential_ids = {
  "pep-snt-prod-scus-global-01-aks-fc" = {     
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"      
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/b8911543-8843-4172-9f0f-862f6e0ef7f1/" 
    subject             = "system:serviceaccount:istio-system:pep-snt-ingress-gw01-service-account"    
    mi_name             = "pep-snt-prod-infra-kv-01-mi" 
  }
}