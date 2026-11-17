federated_credential_ids = {
  "pep-apigee-prod-scus-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/72fb1097-e006-47d9-806a-16c5e3a5433a/"
    subject             = "system:serviceaccount:istio-system:pep-apigee-ingress-gw01-service-account"
    mi_name             = "pep-apigee-prod-infra-kv-01-mi"
  }
}