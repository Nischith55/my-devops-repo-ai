managed_ids = {
  "pep-cmp-nonprod-dmz-eus-01-aks-01-mi" = {
    location            = "eastus"
    resource_group_name = "ess-cv-aks-eus-rg"
    tags = {
      department   = "CMP"
      environment  = "dmz"
      financialTag = "H-######"
      serviceName  = "CMP"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}
