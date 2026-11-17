federated_credential_ids = {
  "pep-fortify-prod-scus-01-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0f275f70-418e-4560-abbf-661fcaaeeea8/"
    subject             = "system:serviceaccount:istio-system:pep-fortify-ingress-gw01-service-account"
    mi_name             = "pep-fortify-prod-infra-kv-01-mi"
  }
}
