federated_credential_ids = {
  "pep-pfna-workload-identity-mi-nonprod-eus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/96087dcd-311d-4f47-9bc7-270e9e4eb02e/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}