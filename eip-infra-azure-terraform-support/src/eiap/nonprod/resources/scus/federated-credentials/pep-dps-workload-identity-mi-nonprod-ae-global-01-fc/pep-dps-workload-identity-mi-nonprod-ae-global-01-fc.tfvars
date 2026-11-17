federated_credential_ids = {
  "pep-dps-workload-identity-mi-nonprod-ae-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://australiaeast.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0cf30f5c-e54b-4664-af16-b0247086ea2a/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-nonprod-infra-kv-01-mi"
  }
}
