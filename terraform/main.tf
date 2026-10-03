module "app_namespace" {
  source       = "./modules/app-namespace"
  namespace    = var.namespace
  app_image    = var.app_image
  app_replicas = var.app_replicas
}
