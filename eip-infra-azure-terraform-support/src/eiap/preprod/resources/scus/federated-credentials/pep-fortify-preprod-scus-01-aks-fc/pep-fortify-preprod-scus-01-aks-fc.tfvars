federated_credential_ids = {
  "pep-fortify-preprod-scus-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/d43ae3ed-d33e-446d-ac1e-16958333017d/"
    subject             = "system:serviceaccount:istio-system:pep-fortify-ingress-gw01-service-account"
    mi_name             = "pep-fortify-nonprod-infra-kv-01-mi"
  }
}
