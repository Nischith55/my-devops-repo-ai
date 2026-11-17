federated_credential_ids = {
  "pep-eiap-prod-sea-infra-02-aks-fc" = {      
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"      
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southeastasia.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/813a8b8f-5401-4cbb-b16e-8bf29bd0b745/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-prod-infra-kv-01-mi"
  }
}