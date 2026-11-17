ase_plan_ids = {
  "pep-eiap-nonprod-gwc-01-ase-plan" = {
    location            = "germanywestcentral"
    resource_group_name = "pep-eiap-nonprod-gwc-ase-01-rg"
    resource_group_name_ase = "pep-eiap-nonprod-gwc-ase-01-rg"
    asev3_name          = "pep-eiap-nonprod-gwc-01-ase"
    os_type             = "Windows"
    sku_name            = "I1v2"
    per_site_scaling_enabled = "false" //Should Per Site Scaling be enabled. Defaults to false.
    zone_balancing_enabled = "false"
    maximum_elastic_worker_count = 1
    worker_count       = 1
    tags = {}
  }
}
