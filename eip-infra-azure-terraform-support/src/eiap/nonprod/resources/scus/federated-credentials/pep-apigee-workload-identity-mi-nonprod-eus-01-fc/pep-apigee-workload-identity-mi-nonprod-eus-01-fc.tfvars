federated_credential_ids = {
  "pep-apigee-workload-identity-mi-nonprod-eus-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/149eaf97-d226-44d7-9329-68d82c3b8d67/"
    subject             = "system:serviceaccount:istio-system:pep-apigee-ingress-gw01-service-account"
    mi_name             = "pep-apigee-nonprod-infra-kv-01-mi"
  }
}
