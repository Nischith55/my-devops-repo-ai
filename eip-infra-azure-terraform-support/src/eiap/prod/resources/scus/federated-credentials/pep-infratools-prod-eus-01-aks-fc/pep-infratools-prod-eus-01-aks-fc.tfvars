federated_credential_ids = {
  "pep-infratools-prod-eus-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/14d4014b-dbab-4134-ab39-3f19b6bae851/"
    subject             = "system:serviceaccount:istio-system:pep-infratools-ingress-gw01-service-account"
    mi_name             = "pep-infratools-prod-infra-kv-01-mi"
  }
}