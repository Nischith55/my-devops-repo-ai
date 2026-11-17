federated_credential_ids = {
  "pep-eiap-workload-identity-mi-aks-fc" = {
    resource_group_name = "pep-eiap-nonprod-eus-k8s-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/b7763898-a63d-48b8-a425-5068d7b8aae5/"
    subject             = "system:serviceaccount:istio-system:pep-eiap-ingress-gw01-service-account"
    mi_name             = "pep-eiap-workload-identity-mi"
  }
}
