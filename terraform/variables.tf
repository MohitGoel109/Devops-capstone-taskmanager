variable "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  type        = string
  default     = "C:/Users/Lenovo/.kube/config"
}

variable "kube_context" {
  description = "kubectl context of the existing kind cluster"
  type        = string
  default     = "kind-capstone"
}

variable "namespace" {
  description = "Namespace for the Task Manager app"
  type        = string
  default     = "taskmanager-tf"
}

variable "app_replicas" {
  description = "Replica count recorded in the ConfigMap"
  type        = number
  default     = 2
}

variable "app_image" {
  description = "Container image recorded in the ConfigMap"
  type        = string
  default     = "taskmanager:local"
}
