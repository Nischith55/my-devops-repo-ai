storage_accounts = {
  pb2001global01aksfp01sa = {
    name                     = "pb2001global01aksfp01sa"
    account_kind             = "FileStorage"
    location                 = "southcentralus"
    resource_group_name      = "pep-pbna-och-k8s-preprod-scus-01-rg"
    account_replication_type = "LRS"
    account_tier             = "Premium"
    tags = {
      department         = "PBNA"
      description        = "preprod pbna storage"
      environment        = "preprod"
      financialTag       = "H-######"
      serviceName        = "pbna"
    }
    allow_nested_items_to_be_public = false
    is_hns_enabled                  = false
    large_file_share_enabled        = true
    network_rules = {
      bypass                     = ["AzureServices", "Logging", "Metrics"]
      default_action             = "Deny"
      ip_rules                   = []
      virtual_network_subnet_ids = ["/subscriptions/f427a039-5122-4a35-ac4a-c63c96d1acde/resourceGroups/pep-network-pbna-preprod-scus-01-rg/providers/Microsoft.Network/virtualNetworks/pep-paas-pbna-preprod-scus-01-vnet/subnets/pep-pbna-aks-global-01-subnet"]
    }
    enable_https_traffic_only = true
    identity_enabled          = []  # specify as ["true"] to enable it
    identity = {
      type         = null
      identity_ids = [] #should be specified in brackets as it is a list
    }
    access_tier                        = "Hot" #default value is Hot; cant be made optional so have to pass it with value as Hot
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
    blob_properties_enabled = [] # specify as [] to disable it
    blob_properties = {
      change_feed_enabled           = true #this must be set to true when versioning_enabled property is true
      change_feed_retention_in_days = 7
      cors_rule_enabled = []
      cors_rule = {
        allowed_headers    = []
        allowed_methods    = []
        allowed_origins    = []
        exposed_headers    = []
        max_age_in_seconds = ""
      }
      container_delete_retention_policy_enabled = [] #specify as ["true"] to enable it
      container_delete_retention_policy_in_days = 0
      delete_retention_policy_enabled = ["true"]
      delete_retention_policy_in_days = 7 #this property depends on delete_retention_policy_enabled
      last_access_time_enabled        = false
      restore_policy_enabled          = ["true"]
      restore_policy_in_days          = 6 #this value should be less than delete_retention_policy property
      versioning_enabled              = true
    }
  }
}

storage_containers = {
}

storage_shares = {
}

storage_encyptions = {
}

storage_queues = {
}

storage_tables = {
}
