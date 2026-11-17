federated_credential_ids = {
  "pep-kafka-cgf-shared-dev-fc" = {
    resource_group_name = "pep-paas-infratools-nonprod-eus-paas-01-rg"
    audience            = ["api://AzureADTokenExchange"]
    issuer              = "https://eastus.oic.prod-aks.azure.com/42cc3295-cd0e-449c-b98e-5ce5b560c1d3/0ac41b8e-1338-4f6a-b0ca-9c5e3baf9074/"
    subject             = "system:serviceaccount:pep-infratools-cgf-shared-dev:pep-infratools-cgf-shared-dev-sa"
    mi_name             = "pep-infratools-nonprod-eus-kafka-01-mi"
  }
}
