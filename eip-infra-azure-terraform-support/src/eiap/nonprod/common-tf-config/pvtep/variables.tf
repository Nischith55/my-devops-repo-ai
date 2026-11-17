variable "private_endpoint" {
  type = map(any)
}

variable "resource_name_to_create" {
  type    = string
}

variable "subscription" {
  type    = string
}

variable "clientid" {
  type    = string
}

variable "clientsecret" {
  type    = string
}

variable "tenantid" {
  type    = string
}