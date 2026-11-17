managed_ids = {
  "pep-eiap-preprod-scus-prometheus-01-mi" = {
    location            = "southcentralus"
    resource_group_name = "pep-eiap-preprod-scus-k8s-01-rg"
    tags = {
        department    = "EIAP",
        description   = "Prometheus MI",
        environment   = "preprod",
        financialTag  = "H-######",
        serviceName   = "EIAP",
        spn           = "pep-eiap-preprod-k8s-sp"
    }
  }
}
