key_vaults = {
  pe1001-cgf-apigee-01-kv = {
    location            = "eastus"
    resource_group_name = "pep-apigee-dev-eus-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = false
    enabled_for_disk_encryption     = false
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 30

    tags = {
      CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-07-12T19:49:37\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-mds42-ddjgg\", \"build\": \"1839675\"}"
      ModifiedData = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-08-17T15:13:08\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-s9brb-sptkw\", \"build\": \"1959531\"}"
      department   = "apigee"
      description  = "Key Vault for Apigee Nonprod"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "apigee"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "28.0.0.0/8"]
      virtual_network_subnet_ids = ["/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-global-01-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-eus-network-01-vnet/subnets/pep-eiap-nonprod-eus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-02-aks-01-snet",
                                    "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-scus-network-01-vnet/subnets/pep-eiap-prod-scus-network-01-vnet-global-01-aks-01-snet",
                                    "/subscriptions/86ddcdc2-9ada-46b9-a53e-dc326f8ecfdc/resourceGroups/pep-network-nonprod-infratools-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-infratools-nonprod-eus-01-vnet/subnets/pep-apigee-dev-aks-01-subnet"
                ]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6b2d415a-5320-49d3-8f55-3fb09034aaea"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"] 
      }
    ]
  }
}