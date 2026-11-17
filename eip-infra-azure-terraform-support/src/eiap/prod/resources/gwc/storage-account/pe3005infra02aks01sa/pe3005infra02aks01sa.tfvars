storage_accounts = {
  pe3005infra02aks01sa = {
    name                     = "pe3005infra02aks01sa"
    account_kind             = "StorageV2"
    location                 = "germanywestcentral"
    resource_group_name      = "pep-eiap-prod-gwc-k8s-01-rg"
    account_replication_type = "ZRS"
    account_tier             = "Standard"
    tags = {
      CreateData   = "{\"ExecuteHost\": \"PEPWUL146726\", \"TimeStamp\": \"2021-02-11T10:56:17\", \"User\": \"09261927\"}"
      department   = "EIAP"
      description  = "GWC SA Infra AKS 02"
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
      ip_rules = ["11.0.0.0/8",
        "142.193.0.0/16",
        "142.65.0.0/16",
        "156.81.0.0/16",
        "156.82.0.0/16",
        "157.146.0.0/16",
        "165.197.0.0/16",
        "165.198.0.0/16",
        "167.27.0.0/16",
        "169.225.0.0/16",
        "192.46.23.0/24",
        "192.46.24.0/21",
        "192.46.32.0/21",
        "192.46.40.0/24",
        "196.6.0.0/20",
        "196.6.16.0/20",
        "196.6.32.0/20",
        "196.6.64.0/24",
        "196.6.90.0/24",
        "198.180.222.0/24",
        "198.180.223.0/24",
        "198.231.17.0/24",
        "198.231.18.0/24",
        "198.231.25.0/24",
        "198.235.0.0/16",
        "199.71.0.0/16",
        "199.88.216.0/21",
        "199.88.224.0/21",
        "204.136.64.0/22",
        "204.154.164.0/22",
        "22.0.0.0/8",
        "26.0.0.0/8",
        "28.0.0.0/8",
        "29.0.0.0/8",
        "30.0.0.0/9",
        "30.144.0.0/14",
        "30.153.0.0/16",
        "30.159.0.0/16",
        "30.176.0.0/14",
        "30.185.0.0/16",
        "30.191.0.0/16",
        "30.192.0.0/14",
        "30.201.0.0/16",
        "30.207.0.0/16",
        "30.64.12.0/23",
        "30.64.14.0/23",
        "5.0.0.0/16",
        "5.1.0.0/16",
        "5.16.0.0/16",
        "5.232.0.0/16",
        "5.233.0.0/16",
        "5.32.0.0/16",
      "7.0.0.0/8"]
      virtual_network_subnet_ids = [
        "/subscriptions/72d4c1b3-fd6e-432a-b18a-89eec2c10a6b/resourceGroups/pep-eiap-prod-gwc-network-01-rg/providers/Microsoft.Network/virtualNetworks/pep-eiap-prod-gwc-network-01-vnet/subnets/pep-eiap-prod-gwc-network-01-vnet-infra-02-aks-01-snet"
      ]
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

    queue_encryption_key_type       = "Service" #default values
    table_encryption_key_type       = "Service" #default values
    default_to_oauth_authentication = false     #default values
    routing_enabled                 = []        #specify as ["true"] to enable it
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
      delete_retention_policy_enabled           = [] #specify as ["true"] to enable it
      delete_retention_policy_in_days           = 0  #this property depends on delete_retention_policy_enabled
      last_access_time_enabled                  = false
      restore_policy_enabled                    = [] #specify as ["true"] to enable it
      restore_policy_in_days                    = 0  #this value should be less than delete_retention_policy property
      versioning_enabled                        = false
    }
  }
}

storage_containers = {
  # "acr-archive-storage" = {
  #   name                  = "acr-archive-storage"
  #   storage_account_name  = "pe1001devsecops01sa"
  #   metadata = {}
  # }
  # azure-devops-agent-01-blob = {
  #   name                  = "azure-devops-agent-01-blob"
  #   storage_account_name  = "pe1001devsecops01sa"
  #   metadata = {
  #     description = "Blob container for storing azure devops agent binaries"
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
