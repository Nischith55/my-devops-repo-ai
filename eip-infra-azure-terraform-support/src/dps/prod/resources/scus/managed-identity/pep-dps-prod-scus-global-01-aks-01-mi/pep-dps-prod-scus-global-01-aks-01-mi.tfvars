managed_ids = {
  "pep-dps-prod-scus-global-01-aks-01-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-dps-k8s-prod-scus-01-rg"
    tags = {
      department   = "DPS"
      environment  = "Prod"
      financialTag = "H-######"
      serviceName  = "DPS"
      spn          = "pep-eiap-prod-k8s-sp"
    }
  }
}
