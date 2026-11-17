managed_ids = {
  "pep-eiap-nonprod-eus-aisp-01-aks-mi" = {
    location            = "eastus"
    resource_group_name = "pep-nonprod-aisp-eus-01-rg"
    tags = {
      department   = "EIAP"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}