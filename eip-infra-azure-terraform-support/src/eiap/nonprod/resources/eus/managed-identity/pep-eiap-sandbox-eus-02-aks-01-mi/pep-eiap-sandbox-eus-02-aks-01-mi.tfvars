managed_ids = {
  "pep-eiap-sandbox-eus-02-aks-01-mi" = {
    location            = "eastus"
    resource_group_name = "pep-aisp-sandbox-eus-k8s-01-rg"

    tags = {
      department   = "EIAP"
      environment  = "sandbox"
      serviceName  = "EIAP"

      financialTag = "H-######"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}
