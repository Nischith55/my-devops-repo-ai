managed_ids = {
  "pep-dps-nonprod-eus-global-01-aks-01-mi" = {
    location            = "eastus"
    resource_group_name = "pep-dps-k8s-nonprod-eus-01-rg"
    tags = {
      department   = "DPS"
      environment  = "NonProd"
      financialTag = "H-######"
      serviceName  = "DPS"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}
