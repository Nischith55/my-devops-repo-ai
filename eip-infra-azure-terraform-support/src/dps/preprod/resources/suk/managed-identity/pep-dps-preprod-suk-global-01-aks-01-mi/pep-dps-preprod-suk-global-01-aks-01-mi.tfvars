managed_ids = {
  "pep-dps-preprod-suk-global-01-aks-01-mi" = {
    location            = "uksouth"
    resource_group_name = "pep-dps-k8s-preprod-suk-01-rg"
    tags = {
        department   = "DPS"
      environment  = "PreProd"
      financialTag = "H-######"
      serviceName  = "DPS"
      spn          = "pep-eiap-preprod-k8s-sp"
    }
  }
}
