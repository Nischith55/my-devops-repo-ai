federated_credential_ids = {
  "pep-snt-workload-identity-mi-preprod-scus-global-01-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/3a0170be-aa0a-4750-8970-fb844c2fa209/"
    subject             = "system:serviceaccount:istio-system:pep-snt-ingress-gw01-service-account"
    mi_name             = "pep-snt-nonprod-infra-kv-01-mi"
  }
}
