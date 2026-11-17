key_vaults = {
  pe1003-cgf-dlops-01-kv = {
    location            = "eastus"
    resource_group_name = "pep-eiap-nonprod-eus-generic-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-10-10T17:56:04\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-nr8bp-vzx49\", \"build\": \"2153278\"}"
      ModifiedData = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-10-10T18:04:09\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-lh5vh-cr7rv\", \"build\": \"2153293\"}"
      department   = "EIAP"
      description  = "Key Vault for DLOPS"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8"]
      virtual_network_subnet_ids = [ "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-backend-01-snet",
                                      "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-global-01-aks-01-snet",
                                      "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-core-01-snet",
                                      "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-01-snet",
                                      "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-02-snet"
                ]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "367dfb5d-8aed-4dcf-9366-6024024bfb94"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      }
    ]
  }
}