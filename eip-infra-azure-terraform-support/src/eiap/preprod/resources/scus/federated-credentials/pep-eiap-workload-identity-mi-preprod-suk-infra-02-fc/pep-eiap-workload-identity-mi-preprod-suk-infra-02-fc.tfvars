federated_credential_ids = {
  "pep-eiap-workload-identity-mi-preprod-suk-infra-02-fc" = {
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://uksouth.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/abb66b2d-7b49-4dcc-b58c-005a57444e43/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-nonprod-infra-kv-01-mi"
  }
}
