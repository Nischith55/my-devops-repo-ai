storage_accounts = {
  pe1001devsecops01sa = {
    name                     = "pe1001devsecops01sa"
    account_kind             = "StorageV2"
    location                 = "southcentralus"
    resource_group_name      = "pep-eiap-nonprod-scus-paas-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      CreateData           = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2021-12-24T12:48:50\", \"User\": \"test\"}"
      ModifiedData         = "{\"ExecuteHost\": \"INPC1F23KR\", \"TimeStamp\": \"2022-06-27T14:54:59\", \"User\": \"chaitanya\"}"
      department           = "EIAP"
      description          = "Azure devops Storage"
      environment          = "nonprod"
      financialTag         = "H-######"
      serviceName          = "EIAP"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass                     = ["AzureServices", "Logging", "Metrics"]
      default_action             = "Deny"
      ip_rules                   = ["103.177.234.72",
                                    "103.246.37.45",
                                    "103.246.37.81",
                                    "136.226.252.84",
                                    "148.64.4.14",
                                    "165.197.0.0/16",
                                    "165.198.0.0/16",
                                    "168.149.152.104", 
                                    "28.0.0.0/8",
                                    "49.207.234.147",
                                    "148.64.4.46",
                                    "49.43.217.171"]
      virtual_network_subnet_ids = [
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-global-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-02-aks-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-core-01-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-infra-services-02-snet",
                  "/subscriptions/154431fe-c911-490e-87a0-c84ced2bee05/resourceGroups/pep-eiap-nonprod-scus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-nonprod-scus-network-01-vnet/subnets/pep-eiap-nonprod-scus-network-01-vnet-paas-pvtlink-01-snet",
                  "/subscriptions/498640c4-36eb-4566-b752-ca3d2939c544/resourceGroups/pep-network-non-prod-pfna-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-pfna-scus-01-vnet/subnets/pep-aks-infra-01-subnet"
                ]
    }
    enable_https_traffic_only = true
    identity_enabled          = []  # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = "Cool" #default value is Hot; cant be made optional so have to pass it with value as Hot
    azure_files_authentication_enabled = []    # specify as ["true"] to enable it
    azure_files_authentication = {
      directory_type      = ""
      storage_sid         = ""
      domain_name         = ""
      domain_sid          = ""
      domain_guid         = ""
      forest_name         = ""
      netbios_domain_name = ""
    }
    custom_domain_enabled = []  # specify as ["true"] to enable it
    custom_domain = {
      name = ""
    }
    nfsv3_enabled   = false
    routing_enabled = []   # specify as ["true"] to enable it
    routing = {
      publish_internet_endpoints  = false              #default values
      publish_microsoft_endpoints = false              #default values
      choice                      = "MicrosoftRouting" #default values
    }
    blob_properties_enabled = ["true"] # specify as [] to disable it
    blob_properties = {
      change_feed_enabled           = false #this must be set to true when versioning_enabled property is true
      change_feed_retention_in_days = null
      cors_rule_enabled = []
      cors_rule = {
        allowed_headers    = []
        allowed_methods    = []
        allowed_origins    = []
        exposed_headers    = []
        max_age_in_seconds = ""
      }

      container_delete_retention_policy_enabled = [] # added
      container_delete_retention_policy_in_days = 0  # added
      delete_retention_policy_enabled = ["true"]
      delete_retention_policy_in_days = 7 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = []
      restore_policy_in_days          = 0 #this value should be less than delete_retention_policy property
      versioning_enabled              = false
    }
  }
}

storage_containers = {
  "acr-archive-storage" = {
    name                  = "acr-archive-storage"
    storage_account_name  = "pe1001devsecops01sa"
    metadata = {}
  }
  azure-devops-agent-01-blob = {
    name                  = "azure-devops-agent-01-blob"
    storage_account_name  = "pe1001devsecops01sa"
    metadata = {
      description = "Blob container for storing azure devops agent binaries"
    }
  }
  azure-aks-secrets = {
    name                  = "azure-aks-secrets"
    storage_account_name  = "pe1001devsecops01sa"
    metadata = {
      description = "Container for storing aks secrets"
    }
  }
}

storage_shares = {
  #set of properties to be used is given below
  # storage_share1 = {
  #   share_name           = ""
  #   storage_account_name = ""
  #   share_quota          = 1
  #   access_tier          = "TransactionOptimized"
  #   enabled_protocol     = "SMB"
  #   metadata             = {}
  #   acl_enabled          = [] # specify as ["true"] to enable it
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = [] # specify as ["true"] to enable it
  #     access_policy = {
  #       permissions = ""
  #       start       = ""
  #       expiry      = ""
  #     }
  #   }
  # }
}

storage_encyptions = {
  #set of properties to be used is given below
  # storage_encrypt_scope1 = {
  #   name                                = ""
  #   storage_account_name                = ""
  #   source                              = "Microsoft.Storage"
  #   infrastructure_encryption_required  = true
  #   key_vault_key_id                    = null
  #   storage_account_resource_group_name = ""
  # }
}

storage_queues = {
  #set of properties to be used is given below
  # storage_queue1 = {
  #   name                 = ""
  #   storage_account_name = ""
  #   metadata             = {}
  # }
}

storage_tables = {
  #set of properties to be used is given below
  # storage_table1 = {
  #   name                 = "testtable"
  #   storage_account_name = ""
  #   acl_enabled          = [] # specify as ["true"] to enable it
  #   acl = {
  #     acl_id                = ""
  #     access_policy_enabled = [] # specify as ["true"] to enable it
  #     access_policy = {
  #       permissions = ""
  #       start       = ""
  #       expiry      = ""
  #     }
  #   }
  # }
}

management_policies = {
  management_policy1 = {
    storage_account_name = "pe1001devsecops01sa"
    storage_account_resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    rules = [
      {
        name    = "rule1"
        enabled = true
        prefix_match               = ["acr-archive-storage/pepeiapnonprodglobal"]
        delete_after_modified_days = 130
      },
      {
        name    = "rule2"
        enabled = true
        prefix_match               = ["acr-archive-storage/pepeiapnonprodcommon"]
        delete_after_modified_days = 130
      }
    ]
  }
}
