module "evh_cg_prod" {
  source                  = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/evh_cgrp"
  evh_consumer_group      = var.evh_consumer_group
  resource_name_to_create = var.resource_name_to_create
  subscription            = var.subscription
  clientid                = var.clientid
  clientsecret            = var.clientsecret
  tenantid                = var.tenantid
}