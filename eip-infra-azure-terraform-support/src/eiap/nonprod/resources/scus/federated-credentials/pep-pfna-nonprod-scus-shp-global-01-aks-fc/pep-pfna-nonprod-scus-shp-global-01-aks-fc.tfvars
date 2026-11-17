federated_credential_ids = {
  "pep-pfna-nonprod-scus-shp-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/8604746e-0a8a-4024-9aa4-7df59f86d020/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-nonprod-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}