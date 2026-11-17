evh_ids = {
  pep-eiap-na-global-infra-poc-perf-01-evh = {
    name                = "pep-eiap-na-global-infra-poc-perf-01-evh"
    namespace_name      = "pep-eiap-nonprod-scus-global-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    partition_count     = 32
    message_retention   = 1
  }
}
evh_authorization_rule = {
  pep-eiap-na-global-infra-poc-perf-01-evh-01-authz = {
    name                = "pep-eiap-na-global-infra-poc-perf-01-evh-01-authz"
    namespace_name      = "pep-eiap-nonprod-scus-global-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    eventhub_name       = "pep-eiap-na-global-infra-poc-perf-01-evh"
    manage              = false
    listen              = true
    send                = true
  }
}
 

 