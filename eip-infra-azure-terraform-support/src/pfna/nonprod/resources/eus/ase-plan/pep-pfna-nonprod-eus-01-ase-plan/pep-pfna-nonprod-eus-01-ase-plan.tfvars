ase_plan_ids = {
  "pep-pfna-nonprod-eus-01-ase" = {
    location            = "eastus"
    resource_group_name = "pep-hhnext-dev-eus-01-rg"
    resource_group_name_ase = "pep-eiap-pfna-ase-nonprod-eus-01-rg"
    asev3_name          = "pep-pfna-nonprod-eus-01-ase"
    os_type             = "Windows"
    sku_name            = "I1v2"
    per_site_scaling_enabled = "false" //Should Per Site Scaling be enabled. Defaults to false.
    zone_balancing_enabled = "false"
    maximum_elastic_worker_count = null
    worker_count       = 1
    tags = {}
  }
}
