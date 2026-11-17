federated_credential_ids = {
  "pep-dps-preprod-suk-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://uksouth.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/69efd9f9-a1b6-4d35-8e62-050adf5dc3ca/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-pfna-nonprod-infra-kv-01-mi"
  }
}