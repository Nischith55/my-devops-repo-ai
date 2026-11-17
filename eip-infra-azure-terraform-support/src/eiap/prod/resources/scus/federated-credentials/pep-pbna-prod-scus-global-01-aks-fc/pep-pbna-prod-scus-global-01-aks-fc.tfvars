federated_credential_ids = {
  "pep-pbna-prod-scus-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/13cbf2e6-1c19-44aa-9a8d-d0c040c0ff73/"
    subject             = "system:serviceaccount:istio-system:pep-pbna-ingress-gw01-service-account"
    mi_name             = "pep-pbna-prod-infra-kv-01-mi"
  }
}