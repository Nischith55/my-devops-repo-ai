key_vaults = {
  pe1001-snt-psd-01-kv = {
    location            = "eastus"
    resource_group_name = "pep-snt-psd-nonprod-eus-01-rg"
    sku_name            = "standard"

    enable_rbac_authorization       = false
    enabled_for_deployment          = true
    enabled_for_disk_encryption     = true
    enabled_for_template_deployment = true
    purge_protection_enabled        = true
    public_network_access_enabled   = true
    soft_delete_retention_days      = 90

    tags = {
      #CreateData   = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-07-12T19:49:37\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-mds42-ddjgg\", \"build\": \"1839675\"}"
      #ModifiedData = "{\"User\": \"neipd999\", \"TimeStamp\": \"2023-08-17T15:13:08\", \"ExecuteHost\": \"pepsico-eip-global-devsecops-agent-batchjob-s9brb-sptkw\", \"build\": \"1959531\"}"
      #department   = "apigee"
      #description  = "Key Vault for Apigee Nonprod"
      #environment  = "nonprod"
      #financialTag = "H-######"
      #serviceName  = "apigee"
    }

    network_acls = {
      bypass                     = "AzureServices"
      default_action             = "Deny"
      ip_rules                   = ["1.6.1.94/32",
                                    "203.122.29.170/32",
                                    "50.47.31.128/32"]
      virtual_network_subnet_ids = ["/subscriptions/cf488406-af15-4248-898e-11932611df2b/resourceGroups/pep-network-nonprod-snt-eus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-snt-01-eus-vnet/subnets/pep-aks-global-01-subnet"
                ]
    }

    access_policies = [
      {
        tenant_id               = "42cc3295-cd0e-449c-b98e-5ce5b560c1d3"
        object_id               = "6b2d415a-5320-49d3-8f55-3fb09034aaea"
        key_permissions         = [ "Get", "List", "Update", "Create", "Import", "Delete", "Recover", "Backup", "Restore", "GetRotationPolicy", "SetRotationPolicy", "Rotate", "Encrypt", "Decrypt", "UnwrapKey", "WrapKey", "Verify", "Sign", "Purge", "Release"]
        secret_permissions      = [ "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore", "Purge"]
        certificate_permissions = ["Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"]
        storage_permissions     = [] 
      }
    ]
  }
}