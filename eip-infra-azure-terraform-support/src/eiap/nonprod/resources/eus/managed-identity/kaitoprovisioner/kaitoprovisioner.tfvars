managed_ids = {
  "kaitoprovisioner" = {
    location            = "eastus"
    resource_group_name = "pep-nonprod-aisp-eus-01-rg"
    tags = {
      department   = "EIAP"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
      spn          = "pep-eiap-nonprod-k8s-sp"
    }
  }
}
