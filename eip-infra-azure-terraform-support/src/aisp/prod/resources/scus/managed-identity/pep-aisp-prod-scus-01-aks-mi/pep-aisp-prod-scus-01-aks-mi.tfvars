managed_ids = {
  "pep-aisp-prod-scus-01-aks-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-aisp-prod-scus-k8s-01-rg"
    tags = {
      department   = "AISP"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "aisp"
      spn          = "pep-eiap-prod-k8s-sp"
    }
  }
}