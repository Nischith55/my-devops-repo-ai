managed_ids = {
  "pep-weblog-nonprod-eus-global-01-aks-01-mi" = {
    location            = "eastus"
    resource_group_name = "pep-eiap-nonprod-eus-sqldba-01-rg"
    tags = {
      department   = "EIAP"
      "description "  = "weblogic-01-poc"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}
