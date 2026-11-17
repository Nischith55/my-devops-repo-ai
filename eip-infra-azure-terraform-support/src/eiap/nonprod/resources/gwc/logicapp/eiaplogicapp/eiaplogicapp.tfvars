logicapp_ids = {
  "eiaplogicapp" = {
    location                      = "germanywestcentral"
    ase_plan_name                 = "pep-eiap-nonprod-gwc-01-ase-plan"
    resource_group_name           = "pep-ecommiq-logicapps-non-prod-gwc-02-rg"
    storage_account_name          = "eiaplogicapppoc"
    client_affinity_enabled       = "false"
    client_certificate_mode       = null   //The mode of the Logic App's client certificates requirement for incoming requests. Possible values are Required and Optional.
    enabled                       = "true" //Is the Logic App enabled? Defaults to true.
    https_only                    = "false" //Can the Logic App only be accessed via HTTPS? Defaults to false.
    app_settings = {
      FUNCTIONS_WORKER_RUNTIME  = "node"
      WEBSITE_VNET_ROUTE_ALL    = 1
      WEBSITE_CONTENTOVERVNET   = 1
      WEBSITE_DNS_SERVER        = "168.63.129.16"
      WEBSITE_NODE_DEFAULT_VERSION = "~16"
    }
    tags         = {}
  }
}