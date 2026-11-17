managed_ids = {
  "pep-automation-prod-scus-01-aks-01-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-ess-automation-aks-prod-scus-01-rg"
    tags = {
      department   = "automation"
      environment  = "Prod"
      financialTag = "H-######"
      serviceName  = "automation"
      spn          = "pep-eiap-prod-k8s-sp"
    }
  }
}
