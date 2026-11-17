federated_credential_ids = {
  "pep-eiap-prod-scus-infra-02-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/2eedc4b2-ab3b-4878-b828-5df6c11b92c2/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-prod-infra-kv-01-mi"
  }
}