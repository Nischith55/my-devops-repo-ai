federated_credential_ids = {
  "pep-cgf-sch-prod-suk-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://uksouth.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0d52e0c0-7eeb-443e-b22d-8b50e187ce5f/"
    subject             = "system:serviceaccount:istio-system:pep-cgf-ingress-gw01-service-account"
    mi_name             = "pep-cgf-prod-infra-kv-01-mi"
  }
}