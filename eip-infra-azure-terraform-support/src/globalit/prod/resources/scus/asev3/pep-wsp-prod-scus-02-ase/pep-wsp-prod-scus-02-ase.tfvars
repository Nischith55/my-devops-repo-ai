asev3_ids = {
  "pep-wsp-prod-scus-02-ase" = {
    location            = "southcentralus"
    resource_group_name = "pep-mypepsicoportal-sucs-01-rg"
    subnet_id           = "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-network-prod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-prod-01-scus-vnet/subnets/pep-ase-03-subnet"
    zone_redundant      = "false"
    allow_new_private_endpoint_connections = "false"
    enable_diagnostic_settings = false
        tags = {
      department   = "Global-IT"
      environment  = "Prod"
      financialTag = "H-######"
      serviceName  = "Global-IT"
      spn          = "pep-eiap-prod-network-sp"
    }
  }
}
