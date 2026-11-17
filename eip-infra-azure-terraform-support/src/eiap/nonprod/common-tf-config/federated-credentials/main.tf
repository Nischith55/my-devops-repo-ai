module "fc_nonprod" {
  source = "git::https://PepsiCoIT@dev.azure.com/PepsiCoIT/EIP-Infrastructure/_git/eip-infra-terraform-modules//modules/mi_federated_credentials"
  federated_credential_ids    = var.federated_credential_ids
  resource_name_to_create     = var.resource_name_to_create
  subscription = var.subscription
  clientid = var.clientid
  clientsecret = var.clientsecret
  tenantid = var.tenantid
}
