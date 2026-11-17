key_vaults = {
  pe2001-prometheus-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-preprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-10-13T16:02:49\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-djb9c-zrtdd\", \"build\": \"2168057\"}"
      department   = "EIAP"
      description  = "Key Vault for Farm 2 Pack"
      environment  = "preprod"
      financialTag = "H-######"
      serviceName  = "eip"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8"]
      virtual_network_subnet_ids = ["/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-scus-network-01-vnet/subnets/pep-eiap-preprod-scus-network-01-vnet-global-01-aks-01-snet",
                                    "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-scus-network-01-vnet/subnets/pep-eiap-preprod-scus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-scus-network-01-vnet/subnets/pep-eiap-preprod-scus-network-01-vnet-infra-core-01-snet"
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