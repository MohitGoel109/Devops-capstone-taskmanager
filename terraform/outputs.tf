output "namespace" {
  description = "Namespace created by Terraform"
  value       = module.app_namespace.namespace
}

output "config_map" {
  description = "ConfigMap created by Terraform"
  value       = module.app_namespace.config_map
}

output "cluster_context" {
  description = "kubectl context Terraform used"
  value       = var.kube_context
}
