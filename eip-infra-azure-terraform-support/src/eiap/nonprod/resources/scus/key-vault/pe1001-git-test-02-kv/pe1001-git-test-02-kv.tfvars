key_vaults = {
  pe1001-git-test-02-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      CreateData   = "{\"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-dxncg-rdmmr\", \"TimeStamp\": \"2023-01-03T05:32:23\", \"User\": \"neipd999\", \"build\": \"1297807\"}"
      ModifiedData = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-05-26T15:14:11\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-424p8-ztt4d\", \"build\": \"1701508\"}"
      department   = "EIAP"
      description  = "Key Vault for testing"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "eip"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8",
                                    "157.51.167.242"
                                    ]
      virtual_network_subnet_ids = ["/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-global-01-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-services-02-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-global-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-core-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-sbox-03-aks-01-snet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "367dfb5d-8aed-4dcf-9366-6024024bfb94"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "e9e1c2e4-aa90-4043-929e-e1bf497c6ba0"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "d04c3d3c-9503-4ad3-bbc5-6160b8e68d29"
        key_permissions         = ["Create", "Get", "List", "Update", "Delete"]
        secret_permissions      = ["Get", "List", "Set", "Delete"]
        certificate_permissions = ["Create", "Get", "List", "Update", "Delete", "Import"]
        storage_permissions     = ["Get", "List", "Update", "Set", "Delete"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "17e4954c-637f-4c1c-bb3a-ff0a6a69a108"
        key_permissions         = ["Create", "Get", "List", "Update", "Delete"]
        secret_permissions      = ["Get", "List", "Set", "Delete"]
        certificate_permissions = ["Create", "Get", "List", "Update", "Delete", "Import"]
        storage_permissions     = ["Get", "List", "Update", "Set", "Delete"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "37a2667c-78e4-4c4e-b12a-7ae558871d9b"
        key_permissions         = ["List"]
        secret_permissions      = ["List"]
        certificate_permissions = ["List"]
        storage_permissions     = ["Get", "List", "Update", "Set", "Delete"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6fbbe4ab-bd63-4a3f-912f-48b7e088319a"
        key_permissions         = ["Get","List"]
        secret_permissions      = ["Get","List"]
        certificate_permissions = ["Get","List"]
        storage_permissions     = ["Get", "List", "Update", "Set", "Delete"] 
      }


    ]
  }
}