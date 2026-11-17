federated_credential_ids = {
  "pep-paas-infratools-workload-identity-mi-nonprod-eus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/43688fe0-0547-4ae9-9924-f4d808e08b8b/"
    subject             = "system:serviceaccount:istio-system:pep-paas-infratools-ingress-gw01-service-account"
    mi_name             = "pep-infratools-nonprod-infra-kv-01-mi"
  }
}