federated_credential_ids = {
  "pep-snt-nonprod-eus-global-01-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/b1a8785a-9542-4955-8ace-68f326c6926a/"
    subject             = "system:serviceaccount:istio-system:pep-snt-ingress-gw01-service-account"
    mi_name             = "pep-snt-nonprod-infra-kv-01-mi"
  }
}