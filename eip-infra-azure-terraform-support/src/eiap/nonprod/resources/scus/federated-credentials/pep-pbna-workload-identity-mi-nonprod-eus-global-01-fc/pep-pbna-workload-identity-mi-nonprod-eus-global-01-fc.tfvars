federated_credential_ids = {
  "pep-pbna-workload-identity-mi-nonprod-eus-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/f1a6ec06-a937-4256-b326-bddc0dad1b26/"
    subject             = "system:serviceaccount:istio-system:pep-pbna-ingress-gw01-service-account"
    mi_name             = "pep-pbna-nonprod-infra-kv-01-mi"
  }
}