asev3_ids = {
  "pep-wsp-nonprod-eus-02-ase" = {
    location            = "eastus"
    resource_group_name = "pep-mypepsicopeople-eus-01-rg"
    subnet_id           = "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-network-nonprod-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-01-eus-vnet/subnets/pep-ase-03-subnet"
    zone_redundant      = "false"
    allow_new_private_endpoint_connections = "false"
    enable_diagnostic_settings = false
        tags = {
      department   = "Global-IT"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "Global-IT"
      spn          = "pep-eiap-nonprod-network-sp"
    }
  }
}
