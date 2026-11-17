evh_ids = {
  pep-eiap-na-global-infra-aks-diag-01-evh = {
    name                = "pep-eiap-na-global-infra-aks-diag-01-evh"
    namespace_name      = "pep-eiap-nonprod-scus-global-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    partition_count     = 20
    message_retention   = 1
  }
}
evh_authorization_rule = {
  pep-eiap-global-infra-aks-diag-send-01 = {
    name                = "pep-eiap-global-infra-aks-diag-send-01"
    namespace_name      = "pep-eiap-nonprod-scus-global-infra-01-evhns"
    resource_group_name = "pep-eiap-nonprod-scus-paas-01-rg"
    eventhub_name       = "pep-eiap-na-global-infra-aks-diag-01-evh"
    manage              = false
    listen              = false
    send                = true
  }
}
 

 