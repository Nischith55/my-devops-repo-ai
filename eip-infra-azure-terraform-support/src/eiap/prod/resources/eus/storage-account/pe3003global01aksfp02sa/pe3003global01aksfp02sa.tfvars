storage_accounts = {
  pe3003global01aksfp02sa = {
    name                     = "pe3003global01aksfp02sa"
    account_kind             = "FileStorage"
    location                 = "eastus"
    resource_group_name      = "pep-eiap-prod-eus-k8s-01-rg"
    account_replication_type = "LRS"
    account_tier             = "Premium"
    tags = {
      CreateData   = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-06-27T16:09:11\", \"User\": \"09261927\"}"
      department   = "EIAP"
      description  = "global-01-aks"
      environment  = "prod"
      financialTag = "H-######"
      serviceName  = "EIAP"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass         = ["AzureServices", "Logging", "Metrics"]
      default_action = "Deny"
      ip_rules       = []
      virtual_network_subnet_ids = [
        "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-eus-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-eus-network-01-vnet/subnets/pep-eiap-prod-eus-network-01-vnet-global-01-aks-01-snet"
      ]
    }
    enable_https_traffic_only = true
    identity_enabled          = [] # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = null #default value is Hot; cant be made optional so have to pass it with value as Hot
    azure_files_authentication_enabled = []   # specify as ["true"] to enable it
    azure_files_authentication = {
      directory_type      = ""
      storage_sid         = ""
      domain_name         = ""
      domain_sid          = ""
      domain_guid         = ""
      forest_name         = ""
      netbios_domain_name = ""
    }
    custom_domain_enabled = [] # specify as ["true"] to enable it
    custom_domain = {
      name = ""
    }
    nfsv3_enabled = false

    routing_enabled = [] # specify as ["true"] to enable it
    routing = {
      publish_internet_endpoints  = false #default values
      publish_microsoft_endpoints = false #default values
      choice                      = null  #default values
    }
    blob_properties_enabled = [] # specify as [] to disable it
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
      container_delete_retention_policy_enabled = [] # added on 25/08/23
      container_delete_retention_policy_in_days = 0  # added on 25/08/23
      delete_retention_policy_enabled           = []
      delete_retention_policy_in_days           = 0 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled                  = false
      restore_policy_enabled                    = []
      restore_policy_in_days                    = 0 #this value should be less than delete_retention_policy property
      versioning_enabled                        = false
    }
  }
}

storage_containers = {
  # insights-logs-networksecuritygroupflowevent = {
  #   name                  = "insights-logs-networksecuritygroupflowevent"
  #   storage_account_name  = "pe1004ctoinfrasa"
  #   metadata = {}
  # }

  # bootdiagnostics-pepldz003-8f0f2c72-f889-4b01-942f-be2f5afd098e = {
  #   name                  = "bootdiagnostics-pepldz003-8f0f2c72-f889-4b01-942f-be2f5afd098e"
  #   storage_account_name  = "pe1004ctoinfrasa"
  #   metadata = {}
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
