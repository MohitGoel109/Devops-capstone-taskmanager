variable "namespace" {
  description = "Namespace to create"
  type        = string
}

variable "app_image" {
  description = "App image recorded in the ConfigMap"
  type        = string
}

variable "app_replicas" {
  description = "Replica count recorded in the ConfigMap"
  type        = number
}
