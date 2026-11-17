federated_credential_ids = {
  "pep-eiap-workload-identity-mi-preprod-eus-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/94cd4340-c866-42f5-8be9-1b55b12cfd53/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-nonprod-infra-kv-01-mi"
  }
}
