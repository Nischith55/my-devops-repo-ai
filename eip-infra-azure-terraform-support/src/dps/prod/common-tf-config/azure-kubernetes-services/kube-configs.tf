resource "local_file" "admin_kubeconfig" {
  filename = "./kubeconfig-admin.kcfg"
  content  = data.azurerm_kubernetes_cluster.cluster_data.kube_admin_config_raw
}

resource "local_file" "user_kubeconfig" {
  filename = "./kubeconfig-user.kcfg"
  content  = data.azurerm_kubernetes_cluster.cluster_data.kube_config_raw
}

data "azurerm_kubernetes_cluster" "cluster_data" {
  provider            = azurerm.data
  name                = var.resource_name_to_create
  resource_group_name = var.cluster_resource_group_name
}

provider "azurerm" {
  alias                      = "data"
  subscription_id            = var.subscription
  client_id                  = var.clientid
  client_secret              = var.clientsecret
  tenant_id                  = var.tenantid
  skip_provider_registration = true
  features {}
}

terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "4.42.0"
    }
  }
}