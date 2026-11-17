federated_credential_ids = {
  "pep-dps-workload-identity-mi-nonprod-eus-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/58df0445-5d2c-4f65-9420-967b18497764/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-nonprod-infra-kv-01-mi"
  }
}