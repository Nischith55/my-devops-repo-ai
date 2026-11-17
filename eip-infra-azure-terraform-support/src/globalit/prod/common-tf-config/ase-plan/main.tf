module "ase_plan_prod" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/ase_plan"
  ase_plan_ids                 = var.ase_plan_ids
  resource_name_to_create     = var.resource_name_to_create
  subscription = var.subscription
  clientid = var.clientid
  clientsecret = var.clientsecret
  tenantid = var.tenantid
}