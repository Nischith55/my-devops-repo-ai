module "asev3_nonprod" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/asev3"
  asev3_ids                 = var.asev3_ids
  resource_name_to_create     = var.resource_name_to_create
  subscription = var.subscription
  clientid = var.clientid
  clientsecret = var.clientsecret
  tenantid = var.tenantid
}