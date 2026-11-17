storage_accounts = {
  pd1007dpsglobal01aks01sa = {
    name                     = "pd1007dpsglobal01aks01sa"
    account_kind             = "StorageV2"
    location                 = "australiaeast"
    resource_group_name      = "pep-dps-nonprod-ae-k8s-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      department   = "DPS"
      description  = "global-01-aks"
      environment  = "nonprod"
      financialTag = "H-######"
      serviceName  = "DPS"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass         = ["AzureServices", "Logging", "Metrics"]
      default_action = "Deny"
      ip_rules       = ["165.197.0.0/16", "165.198.0.0/16", "28.0.0.0/8"]
      virtual_network_subnet_ids = ["/subscriptions/93c33431-a080-4b4a-a362-3b7c5a36b6dc/resourceGroups/pep-network-nonprod-snt-dps-ae-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-nonprod-snt-dps-01-ae-vnet/subnets/pep-aks-global-01-subnet"]
    }
    enable_https_traffic_only = true
    identity_enabled          = [] #specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = "Hot" #default value is Hot; cant be made optional so have to pass it with value as Hot
    azure_files_authentication_enabled = []    #specify as ["true"] to enable it
    azure_files_authentication = {
      directory_type      = ""
      storage_sid         = ""
      domain_name         = ""
      domain_sid          = ""
      domain_guid         = ""
      forest_name         = ""
      netbios_domain_name = ""
    }
    custom_domain_enabled = [] #specify as ["true"] to enable it
    custom_domain = {
      name = ""
    }
    nfsv3_enabled = false
    routing_enabled = [] #specify as ["true"] to enable it
    routing = {
      publish_internet_endpoints  = false              #default values
      publish_microsoft_endpoints = false              #default values
      choice                      = "MicrosoftRouting" #default values
    }
    blob_properties_enabled = ["true"] #specify as [] to disable it
    blob_properties = {
      change_feed_enabled           = false #this must be set to true when versioning_enabled property is true
      change_feed_retention_in_days = null
      cors_rule_enabled             = []
      cors_rule = {
        allowed_headers    = []
        allowed_methods    = []
        allowed_origins    = []
        exposed_headers    = []
        max_age_in_seconds = ""
      }
      container_delete_retention_policy_enabled = [] #specify as ["true"] to enable it
      container_delete_retention_policy_in_days = 0
      delete_retention_policy_enabled = [] #specify as ["true"] to enable it
      delete_retention_policy_in_days = 0  #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = [] #specify as ["true"] to enable it
      restore_policy_in_days          = 0  #this value should be less than delete_retention_policy property
      versioning_enabled              = false
    }
  }
}

storage_containers = {
  # cmp-storage-container = {
  #   name                  = "cmp-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for CMP functional area"
  #   }
  # }
  # edap-storage-container = {
  #   name                  = "edap-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for EDAP functional area"
  #   }
  # }
  # eiap-storage-container = {
  #   name                  = "eiap-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for EIAP functional area"
  #   }
  # }
  # infratools-storage-container = {
  #   name                  = "infratools-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for INFRATOOLS functional area"
  #   }
  # }
  # pfna-storage-container = {
  #   name                  = "pfna-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for PFNA functional area"
  #   }
  # }
  # snt-storage-container = {
  #   name                  = "snt-storage-container"
  #   storage_account_name  = "pe1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for SNT functional area"
  #   }
  # }
  # dps-storage-container = {
  #   name                  = "dps-storage-container"
  #   storage_account_name  = "pd1007auto01tf01sa"
  #   metadata = {
  #     description = "storage container for tf state file for DPS functional area"
  #   }
  # }
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
