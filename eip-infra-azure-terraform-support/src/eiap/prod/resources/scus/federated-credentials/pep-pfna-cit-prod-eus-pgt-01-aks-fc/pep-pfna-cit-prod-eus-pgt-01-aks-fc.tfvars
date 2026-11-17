federated_credential_ids = {
  "pep-pfna-cit-prod-eus-pgt-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/a7b74f2b-c62d-4373-bb00-422d1044c46d/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-prod-infra-kv-01-mi"
  }
}
