logicapp_ids = {
  "pep-pfna-ase-nonprod-eus-logicapp" = {
    location                      = "eastus"
    ase_plan_name                 = "pep-pfna-nonprod-eus-01-ase-plan"
    resource_group_name           = "pep-hhnext-dev-eus-01-rg"
    storage_account_name          = "pfnaeiapasesa"
    client_affinity_enabled       = "false"
    client_certificate_mode       = null   //The mode of the Logic App's client certificates requirement for incoming requests. Possible values are Required and Optional.
    enabled                       = "true" //Is the Logic App enabled? Defaults to true.
    https_only                    = "false" //Can the Logic App only be accessed via HTTPS? Defaults to false.
    app_settings = {
      FUNCTIONS_WORKER_RUNTIME  = "node"
      WEBSITE_VNET_ROUTE_ALL    = 1
    }
    tags         = {}
  }
}