output "namespace" {
  description = "Name of the created namespace"
  value       = kubernetes_namespace.app.metadata[0].name
}

output "config_map" {
  description = "Name of the app ConfigMap"
  value       = kubernetes_config_map.app.metadata[0].name
}
