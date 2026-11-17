federated_credential_ids = {
  "pep-pfna-cit-prod-scus-infra-02-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/9808442d-502f-46c4-b0d3-0e167864ce0f/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-prod-infra-kv-01-mi"
  }
}