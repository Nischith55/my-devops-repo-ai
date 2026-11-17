federated_credential_ids = {
  "pep-dps-workload-identity-mi-nonprod-gwc-global-01" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://germanywestcentral.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/06d0f555-d6d9-4b60-ae38-f735490e5fea/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-nonprod-infra-kv-01-mi"
  }
}