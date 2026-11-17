evh_ids = {
  pep-eiap-prod-suk-global-infra-aks-diag-01-evh = {
    name                = "pep-eiap-prod-suk-global-infra-aks-diag-01-evh"
    namespace_name      = "pep-eiap-prod-suk-monitoring-01-evhns"
    resource_group_name = "pep-eiap-prod-suk-paas-01-rg"
    partition_count     = 32
    message_retention   = 7
  }
}
evh_authorization_rule = {
  ElasticBeatListenerAccessKey = {
    name                = "ElasticBeatListenerAccessKey"
    namespace_name      = "pep-eiap-prod-suk-monitoring-01-evhns"
    resource_group_name = "pep-eiap-prod-suk-paas-01-rg"
    eventhub_name       = "pep-eiap-prod-suk-global-infra-aks-diag-01-evh"
    manage              = false
    listen              = true
    send                = true
  }
}
 