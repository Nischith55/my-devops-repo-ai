variable "storage_accounts" {
  type = map(any)
}

variable "storage_containers" {
  type = map(any)
}

variable "resource_name_to_create" {
   type = string
 }

variable "subscription" {
   type = string
 }

variable "clientid" {
   type = string
 }

variable "clientsecret" {
   type = string
 }

variable "tenantid" {
   type = string
 }

variable "storage_shares" {
  type = map(any)
}

variable "storage_encyptions" {
  type = map(any)
}

variable "storage_queues" {
  type = map(any)
}

variable "storage_tables" {
  type = map(any)
}

variable "management_policies" {
  type = map(any)
  default = {}
}