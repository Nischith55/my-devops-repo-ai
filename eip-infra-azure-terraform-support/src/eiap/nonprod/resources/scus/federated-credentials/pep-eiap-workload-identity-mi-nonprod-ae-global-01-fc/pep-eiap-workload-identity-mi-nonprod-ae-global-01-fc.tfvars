federated_credential_ids = {
  "pep-eiap-workload-identity-mi-nonprod-ae-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://australiaeast.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/ef363659-9e7e-455d-b495-0ef7c29ee9b7/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-nonprod-infra-kv-01-mi"
  }
}
