federated_credential_ids = {
  "pep-pfna-nonprod-eus-shp-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/d603e9ef-4eca-4b2e-90c7-1fd8f820360c/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-nonprod-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}