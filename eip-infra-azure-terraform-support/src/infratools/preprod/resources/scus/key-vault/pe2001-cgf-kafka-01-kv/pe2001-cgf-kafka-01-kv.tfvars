key_vaults = {
  pe2001-cgf-kafka-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-paas-infratools-preprod-scus-paas-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      department   = "infratools"
      description  = "Key Vault for kafka Preprod"
      environment  = "preprod"
      financialTag = "H-######"
      serviceName  = "infratools"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8"]
      virtual_network_subnet_ids = ["/subscriptions/86ddcdc2-9ada-46b9-a53e-dc326f8ecfdc/resourceGroups/pep-network-nonprod-infratools-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-infratools-nonprod-scus-01-vnet/subnets/pep-kafka-nonprod-scus-aks-01-subnet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-eus-network-01-vnet/subnets/pep-eiap-preprod-eus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/8a22bd18-1080-472c-a8af-da15be88b076/resourceGroups/pep-eiap-preprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-preprod-scus-network-01-vnet/subnets/pep-eiap-preprod-scus-network-01-vnet-infra-02-aks-01-snet"
                ]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "d8918636-45e6-4ace-8ea8-fd7ec17ceff9"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "50fc4309-6152-4087-b112-8e41494cbc84"
        key_permissions         = ["Create", "Get", "List", "Update", "Delete"]
        secret_permissions      = ["Get", "List", "Set", "Delete"]
        certificate_permissions = ["Create", "Get", "List", "Update", "Delete", "Import"]
        storage_permissions     = ["Get", "List", "Update", "Set", "Delete"] 
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
        object_id               = "78294bc6-1c33-40c2-bdb1-ebdcee4dbbbf"
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "3769d25b-fcb4-4a6e-b4af-038b638837ca"
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "44d4829a-58da-4533-95de-404f6940aafd"
        key_permissions         = ["Get", "List"]
        secret_permissions      = ["Get", "List"]
        certificate_permissions = ["Get", "List"]
        storage_permissions     = ["Get", "List"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "f748990b-37e4-45a3-8fc8-37985b73780d"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      },
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6b922ae7-a185-48e9-9e7e-ec5bb6f67b95"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      }
    ]
  }
}