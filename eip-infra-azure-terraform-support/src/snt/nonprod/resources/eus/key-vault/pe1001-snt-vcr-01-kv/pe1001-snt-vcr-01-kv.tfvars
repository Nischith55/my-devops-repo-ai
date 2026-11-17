key_vaults = {
  pe1001-snt-vcr-01-kv = {
    location            = "eastus"
    resource_group_name = "pep-snt-vcr-nonprod-eus-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 90

    tags = {
      #department   = "apigee"
      #description  = "Key Vault for Apigee Nonprod"
      #environment  = "nonprod"
      #financialTag = "H-######"
      #serviceName  = "apigee"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/cf488406-af15-4248-898e-11932611df2b/resourceGroups/pep-network-nonprod-snt-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-snt-01-eus-vnet/subnets/pep-aks-global-01-subnet"]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "925e8850-6d47-4e32-af9d-d735c1d420ed"
        key_permissions         = [ "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate", "Encrypt", "Decrypt", "UnwrapKey", "WrapKey", "Verify", "Sign", "Release"]
        secret_permissions      = [ "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
        certificate_permissions = [ "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "ManageContacts", "ManageIssuers", "GetIssuers", "ListIssuers", "SetIssuers", "DeleteIssuers", "Purge"]
        storage_permissions     = [] 
      }
    ]
  }
}