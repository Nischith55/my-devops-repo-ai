managed_ids = {
  "pep-aisp-preprod-scus-02-aks-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-preprod-scus-k8s-01-rg"
    tags = {
      department   = "AISP"
      environment  = "preprod"
      financialTag = "H-######"
      serviceName  = "aisp"
      spn          = "pep-eiap-preprod-k8s-sp"
    }
  }
}