federated_credential_ids = {
  "pep-pfna-cit-prod-scus-pcaf-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/866d6b62-e3c8-4745-86c2-ea815860d9a0/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-prod-infra-kv-01-mi"
  }
}