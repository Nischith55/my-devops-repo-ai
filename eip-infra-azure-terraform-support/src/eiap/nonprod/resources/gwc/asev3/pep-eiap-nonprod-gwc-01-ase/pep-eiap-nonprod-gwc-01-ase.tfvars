asev3_ids = {
  "pep-eiap-nonprod-gwc-01-ase" = {
    location            = "germanywestcentral"
    resource_group_name = "pep-eiap-nonprod-gwc-ase-01-rg"
    subnet_id           = "/subscriptions/0c1319a6-1def-4d09-a0ca-46d9b0812fbd/resourceGroups/pep-network-non-prod-europe-gwc-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-europe-nonprod-gwc-01-vnet/subnets/pep-ase-01-subnet"
    zone_redundant      = "false"
    allow_new_private_endpoint_connections = "true" //Should new Private Endpoint Connections be allowed. Defaults to true.
    dedicated_host_count = 0
    tags = {
      env  = "nonprod"
    }
  }
}
