federated_credential_ids = {
  "pep-eiap-preprod-scus-prometheus-01-fc" = {
    resource_group_name = "pep-eiap-preprod-scus-k8s-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/a9be35d1-9534-4b67-b490-999bc7e9e70d/"
    subject             = "system:serviceaccount:prometheus:prometheus-sa"
    mi_name             = "pep-eiap-preprod-scus-prometheus-01-mi"
  }
}
