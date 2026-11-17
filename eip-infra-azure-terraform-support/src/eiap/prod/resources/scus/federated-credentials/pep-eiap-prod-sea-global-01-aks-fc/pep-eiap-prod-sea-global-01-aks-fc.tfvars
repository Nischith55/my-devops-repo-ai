federated_credential_ids = {
  "pep-eiap-prod-sea-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southeastasia.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/e024540d-4d7f-4298-9212-f65246e5827e/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-prod-infra-kv-01-mi"
  }
}