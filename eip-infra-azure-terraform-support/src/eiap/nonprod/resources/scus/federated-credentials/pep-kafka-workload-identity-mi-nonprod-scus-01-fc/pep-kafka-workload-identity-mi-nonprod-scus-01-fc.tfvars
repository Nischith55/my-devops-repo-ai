federated_credential_ids = {
  "pep-kafka-workload-identity-mi-nonprod-scus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/9a4e28a9-60de-4028-b3c1-d9013b923176/"
    subject             = "system:serviceaccount:istio-system:pep-kafka-ingress-gw01-service-account"
    mi_name             = "pep-kafka-nonprod-infra-kv-01-mi"
  }
}
