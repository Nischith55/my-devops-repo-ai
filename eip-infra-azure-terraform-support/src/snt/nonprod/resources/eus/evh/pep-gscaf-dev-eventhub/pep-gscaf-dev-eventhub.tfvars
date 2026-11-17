evh_ids = {
  pep-gscaf-dev-eventhub = {
    name                = "pep-gscaf-dev-eventhub"
    namespace_name      = "pep-dps-nonprod-eus-eventhub-01-evhns"
    resource_group_name = "pep-snt-b2bso-nonprod-eus-01-rg"
    partition_count     = 2
    message_retention   = 1
  }
}
evh_authorization_rule = {
  gscaf = {
    name                = "gscaf"
    namespace_name      = "pep-dps-nonprod-eus-eventhub-01-evhns"
    resource_group_name = "pep-snt-b2bso-nonprod-eus-01-rg"
    eventhub_name       = "pep-gscaf-dev-eventhub"
    manage              = true
    listen              = true
    send                = true
  }
}
