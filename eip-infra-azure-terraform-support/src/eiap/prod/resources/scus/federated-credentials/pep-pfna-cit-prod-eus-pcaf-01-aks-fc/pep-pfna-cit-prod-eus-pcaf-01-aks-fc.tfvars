federated_credential_ids = {
  "pep-pfna-cit-prod-eus-pcaf-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0752a7c3-aabf-4284-b74c-68dfe3ab3a9a/"
    subject             = "system:serviceaccount:istio-system:pep-pfna-ingress-gw01-service-account"
    mi_name             = "pep-pfna-prod-infra-kv-01-mi"
  }
}