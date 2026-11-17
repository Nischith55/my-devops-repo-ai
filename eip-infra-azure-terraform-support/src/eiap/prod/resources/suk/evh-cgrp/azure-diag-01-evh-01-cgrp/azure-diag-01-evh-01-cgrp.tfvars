evh_consumer_group = {
  azure-diag-01-evh-01-cgrp = {
    name                = "azure-diag-01-evh-01-cgrp"
    namespace_name      = "pep-eiap-prod-suk-monitoring-01-evhns"
    resource_group_name = "pep-eiap-prod-suk-paas-01-rg"
    eventhub_name       = "pep-eiap-prod-suk-global-infra-aks-diag-01-evh"
    user_metadata       = "Filebeat Azure Module"
  }
}  