asev3_ids = {
  "pep-pfna-nonprod-eus-01-ase" = {
    location            = "eastus"
    resource_group_name = "pep-eiap-pfna-ase-nonprod-eus-01-rg"
    subnet_id           = "/subscriptions/498640c4-36eb-4566-b752-ca3d2939c544/resourceGroups/pep-network-non-prod-pfna-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-pfna-eus-01-vnet/subnets/pep-ase-01-subnet"
    zone_redundant      = "false"
    allow_new_private_endpoint_connections = "false"
    tags = {
      department   = "PFNA"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "PFNA"
      spn          = "pep-eiap-nonprod-network-sp"
    }
  }
}
