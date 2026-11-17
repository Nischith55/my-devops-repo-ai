federated_credential_ids = {
  "pep-dps-prod-sea-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southeastasia.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/a8801aa9-c233-40d0-afb9-956f8f6ef541/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-prod-infra-kv-01-mi"
  }
}