federated_credential_ids = {
  "pep-arize-nonprod-eus-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/64d4ad60-3831-46ce-a104-6fed41057e5d/"
    subject             = "system:serviceaccount:istio-system:pep-infratools-ingress-gw01-service-account"
    mi_name             = "pep-arize-nonprod-infra-kv-01-mi"
  }
}