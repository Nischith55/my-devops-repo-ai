managed_ids = {
  "pep-dps-preprod-scus-global-01-aks-01-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-dps-k8s-preprod-scus-01-rg"
    tags = {
      department   = "DPS"
      environment  = "PreProd"
      financialTag = "H-######"
      serviceName  = "DPS"
      spn          = "pep-eiap-preprod-k8s-sp"
    }
  }
}
