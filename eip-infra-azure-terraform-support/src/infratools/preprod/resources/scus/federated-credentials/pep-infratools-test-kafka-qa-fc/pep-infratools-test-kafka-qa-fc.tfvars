federated_credential_ids = {
  "pep-infratools-test-kafka-qa-fc" = {
    resource_group_name = "pep-paas-infratools-preprod-scus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://southcentralus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/9a4e28a9-60de-4028-b3c1-d9013b923176/"
    subject             = "system:serviceaccount:pep-infratools-test-kafka-qa:pep-infratools-test-kafka-qa-sa"
    mi_name             = "pep-infratools-preprod-scus-kafka-01-mi"
  }
}