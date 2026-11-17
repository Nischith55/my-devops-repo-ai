federated_credential_ids = {
  "pep-kafka-workload-identity-mi-nonprod-eus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0ac41b8e-1338-4f6a-b0ca-9c5e3baf9074/"
    subject             = "system:serviceaccount:istio-system:pep-kafka-ingress-gw01-service-account"
    mi_name             = "pep-kafka-nonprod-infra-kv-01-mi"
  }
}