federated_credential_ids = {
  "pep-cgf-workload-identity-mi-nonprod-gwc-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://germanywestcentral.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/8311e5c8-7206-4835-b7bb-16aa96db4488/"
    subject             = "system:serviceaccount:istio-system:pep-cgf-ingress-gw01-service-account"
    mi_name             = "pep-cgf-nonprod-infra-kv-01-mi"
  }
}