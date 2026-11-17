key_vaults = {
  pe1001-cgf-dop-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      CreateData   = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-01-31T19:30:25\", \"User\": \"09261927\"}"
      ModifiedData = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-02-22T21:23:24\", \"User\": \"09261927\"}"
      department   = "EIAP"
      description  = "Key Vault for DOP (Distributed Order Portal)"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "EIAP"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8"
                                    ]
      virtual_network_subnet_ids = ["/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-02-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-global-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-core-01-snet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "367dfb5d-8aed-4dcf-9366-6024024bfb94"
        key_permissions         = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "Decrypt",
                                   "Encrypt",
                                   "UnwrapKey",
                                   "WrapKey",
                                   "Verify",
                                   "Sign",
                                   "Release",
                                   "Rotate",
                                   "GetRotationPolicy",
                                   "SetRotationPolicy"]
        secret_permissions      = ["Get",
                                   "List",
                                   "Set",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore"]
        certificate_permissions = ["Get",
                                   "List",
                                   "Update",
                                   "Create",
                                   "Import",
                                   "Delete",
                                   "Recover",
                                   "Backup",
                                   "Restore",
                                   "ManageContacts",
                                   "ManageIssuers",
                                   "GetIssuers",
                                   "ListIssuers",
                                   "SetIssuers",
                                   "DeleteIssuers"]
        storage_permissions     = ["Backup", 
                                   "Delete", 
                                   "DeleteSAS", 
                                   "Get", 
                                   "GetSAS", 
                                   "List", 
                                   "ListSAS", 
                                   "Purge", 
                                   "Recover", 
                                   "RegenerateKey", 
                                   "Restore", 
                                   "Set", 
                                   "SetSAS", 
                                   "Update"] 
      }
    ]
  }
}