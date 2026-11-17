federated_credential_ids = {
  "pep-dps-preprod-scus-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/a26de4d6-c3eb-4935-a2b8-770b9d86d160/"
    subject             = "system:serviceaccount:istio-system:pep-dps-ingress-gw01-service-account"
    mi_name             = "pep-dps-nonprod-infra-kv-01-mi"
  }
}