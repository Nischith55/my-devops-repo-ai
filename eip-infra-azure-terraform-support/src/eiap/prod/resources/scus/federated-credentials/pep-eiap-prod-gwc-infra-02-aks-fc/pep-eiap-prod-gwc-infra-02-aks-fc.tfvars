federated_credential_ids = {
  "pep-eiap-prod-gwc-infra-02-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://germanywestcentral.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/75b70e2e-bfe8-478c-98e8-a2870d36a78f/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-prod-infra-kv-01-mi"
  }
}