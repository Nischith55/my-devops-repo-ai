key_vaults = {
  pe2001-snt-vcr-01-kv = {
    location            = "southcentralus"
    resource_group_name = "pep-snt-vcr-preprod-scus-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 90

    tags = {
      #CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-10-13T16:02:49\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-djb9c-zrtdd\", \"build\": \"2168057\"}"
      #department   = "EIAP"
      #description  = "Key Vault for Farm 2 Pack"
      #environment  = "preprod"
      #financialTag = "H-######"
      #serviceName  = "eip"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/cf488406-af15-4248-898e-11932611df2b/resourceGroups/pep-network-nonprod-snt-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-snt-01-scus-vnet/subnets/pep-aks-global-01-subnet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "925e8850-6d47-4e32-af9d-d735c1d420ed"
        key_permissions         = ["Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "GetRotationPolicy"]
        secret_permissions      = ["Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = ["Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Purge", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"]
      }
    ]
  }
}