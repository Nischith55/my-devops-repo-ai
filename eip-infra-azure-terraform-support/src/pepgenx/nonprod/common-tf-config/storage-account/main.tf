module "sa_nonprod" {
  source                  = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/storage_account"
  storage_accounts        = var.storage_accounts
  storage_containers      = var.storage_containers
  storage_shares          = var.storage_shares
  storage_encyptions      = var.storage_encyptions
  storage_queues          = var.storage_queues
  storage_tables          = var.storage_tables
  resource_name_to_create = var.resource_name_to_create
  subscription            = var.subscription
  clientid                = var.clientid
  clientsecret            = var.clientsecret
  tenantid                = var.tenantid
}
