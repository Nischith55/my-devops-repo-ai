federated_credential_ids = {
  "pep-eiap-workload-identity-mi-nonprod-eus-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/8b6b3614-fd6f-407f-93fc-4060b69062b0/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-nonprod-infra-kv-01-mi"
  }
}