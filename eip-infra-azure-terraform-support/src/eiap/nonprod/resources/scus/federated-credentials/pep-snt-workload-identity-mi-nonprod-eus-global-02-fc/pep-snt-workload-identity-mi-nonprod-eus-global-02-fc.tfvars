federated_credential_ids = {
  "pep-snt-workload-identity-mi-nonprod-eus-global-02-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/42fd4338-445a-49a7-a641-8702b70c8a72/"
    subject             = "system:serviceaccount:istio-system:pep-snt-ingress-gw01-service-account"
    mi_name             = "pep-snt-nonprod-infra-kv-01-mi"
  }
}
