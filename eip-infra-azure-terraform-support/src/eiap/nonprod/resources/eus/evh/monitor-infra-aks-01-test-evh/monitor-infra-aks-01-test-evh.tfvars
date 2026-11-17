evh_ids = {
  monitor-infra-aks-01-test-evh = {
    name                = "monitor-infra-aks-01-test-evh"
    namespace_name      = "pep-eiap-nonprod-eus-test-01-evhns"
    resource_group_name = "pep-eiap-nonprod-eus-pcf-01-rg"
    partition_count     = 20
    message_retention   = 1
  }
}
evh_authorization_rule = {
  aks-monitor-send-01-test-evh-authz = {
    name                = "aks-monitor-send-01-test-evh-authz"
    namespace_name      = "pep-eiap-nonprod-eus-test-01-evhns"
    resource_group_name = "pep-eiap-nonprod-eus-pcf-01-rg"
    eventhub_name       = "monitor-infra-aks-01-test-evh"
    manage              = false
    listen              = false
    send                = true
  }
}