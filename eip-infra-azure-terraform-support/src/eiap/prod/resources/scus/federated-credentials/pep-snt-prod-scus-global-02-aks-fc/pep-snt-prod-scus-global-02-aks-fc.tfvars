federated_credential_ids = {
  "pep-snt-prod-scus-global-02-aks-fc" = {
    resource_group_name = "pep-eiap-prod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/ccc2ce93-ca4e-4d22-a759-d77edce22071/"
    subject             = "system:serviceaccount:istio-system:pep-snt-ingress-gw01-service-account"
    mi_name             = "pep-snt-prod-infra-kv-01-mi"
  }
}