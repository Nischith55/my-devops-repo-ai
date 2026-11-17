federated_credential_ids = {
  "pep-apigee-prod-eus-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/6de848f1-5194-43eb-955c-36f412e643ff/"
    subject             = "system:serviceaccount:istio-system:pep-apigee-ingress-gw01-service-account"
    mi_name             = "pep-apigee-prod-infra-kv-01-mi"
  }
}
