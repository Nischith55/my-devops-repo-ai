federated_credential_ids = {
  "pep-pepgenx-dev-workload-identity-mi-nonprod-eus-01-fc" = {
    resource_group_name = "pep-azr-pepgenx2-shared-dev-eus-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/666b581f-7d75-4e42-b320-2d0846e5bb4c/"
    subject             = "system:serviceaccount:istio-system:istio-ingressgateway-service-account"
    mi_name             = "pep-pepgenx-nonprod-dev-kv-01-mi"
  }
}