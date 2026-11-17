ase_plan_ids = {
  "pep-mypepsico-dev-eus-01-asp" = {
    location            = "eastus"
    resource_group_name = "pep-mypepsicopeople-eus-01-rg"
    resource_group_name_ase = "pep-mypepsicopeople-eus-01-rg"
    asev3_name          = "pep-wsp-nonprod-eus-02-ase"
    os_type             = "Linux"
    sku_name            = "I1v2"
    per_site_scaling_enabled = "false" //Should Per Site Scaling be enabled. Defaults to false.
    zone_balancing_enabled = "false"
    maximum_elastic_worker_count = null
    enable_diagnostic_settings = false
    worker_count       = 1
    tags = {}
  }
}
