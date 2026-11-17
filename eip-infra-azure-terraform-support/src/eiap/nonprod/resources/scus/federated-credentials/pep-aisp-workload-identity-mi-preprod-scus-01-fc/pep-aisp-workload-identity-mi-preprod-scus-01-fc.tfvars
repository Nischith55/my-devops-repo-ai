federated_credential_ids = {
  "pep-aisp-workload-identity-mi-preprod-scus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/4152d7fc-9135-4676-b5f5-be5d26eaf0a8/"
    subject             = "system:serviceaccount:istio-system:pep-aisp-ingress-gw01-service-account"
    mi_name             = "pep-aisp-nonprod-infra-kv-01-mi"
  }
}