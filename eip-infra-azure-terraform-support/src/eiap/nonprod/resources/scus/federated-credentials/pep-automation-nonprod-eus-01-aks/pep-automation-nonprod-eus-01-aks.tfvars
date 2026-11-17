federated_credential_ids = {
  "pep-automation-nonprod-eus-01-aks" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/d3345dc5-4ef2-4e08-9409-90ae4e22b6f5/"
    subject             = "system:serviceaccount:istio-system:pep-automation-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}