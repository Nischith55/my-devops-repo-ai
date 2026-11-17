federated_credential_ids = {
  "pep-pbna-preprod-scus-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/f7aba6ed-a40f-44e6-be3c-849ed7c3c777/"
    subject             = "system:serviceaccount:istio-system:pep-pbna-ingress-gw01-service-account"
    mi_name             = "pep-pbna-nonprod-infra-kv-01-mi"
  }
}