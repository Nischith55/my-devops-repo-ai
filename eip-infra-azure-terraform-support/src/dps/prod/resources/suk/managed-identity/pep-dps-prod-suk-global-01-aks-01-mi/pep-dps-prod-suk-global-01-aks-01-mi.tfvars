managed_ids = {
  "pep-dps-prod-suk-global-01-aks-01-mi" = {
    location            = "uksouth"
    resource_group_name = "pep-dps-prod-suk-k8s-01-rg"
    tags = {
      department   = "DPS"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "DPS"
      spn          = "pep-eiap-prod-k8s-sp"
    }
  }
}
