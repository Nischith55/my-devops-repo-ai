federated_credential_ids = {
  "pep-apigee-preprod-scus-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/41a542ae-348c-4660-bc17-6907a1d6f3dc/"
    subject             = "system:serviceaccount:istio-system:pep-apigee-ingress-gw01-service-account"
    mi_name             = "pep-apigee-nonprod-infra-kv-01-mi"
  }
}