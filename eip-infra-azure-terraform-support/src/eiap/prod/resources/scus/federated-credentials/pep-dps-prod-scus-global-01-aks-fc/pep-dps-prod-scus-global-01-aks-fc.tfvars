federated_credential_ids = {
  "pep-dps-prod-scus-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/adfa3c8c-f5bf-4740-8f36-eaa63c577b8a/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-prod-infra-kv-01-mi"
  }
}