federated_credential_ids = {
  "pep-infratools-prod-scus-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/13ca67bc-eee3-4a8d-93d5-1639e3dd7b71/"
    subject             = "system:serviceaccount:istio-system:pep-infratools-ingress-gw01-service-account"
    mi_name             = "pep-infratools-prod-infra-kv-01-mi"
  }
}