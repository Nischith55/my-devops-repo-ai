federated_credential_ids = {
  "pep-cmp-nonprod-eus-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/c40a9d70-1e68-4967-8ec3-0c6bd9577a01/"
    subject             = "system:serviceaccount:istio-system:pep-cmp-ingress-gw01-service-account"
    mi_name             = "pep-cmp-nonprod-infra-kv-01-mi"
  }
}
