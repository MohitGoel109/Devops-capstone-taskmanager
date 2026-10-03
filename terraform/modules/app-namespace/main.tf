terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
  }
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace
    labels = {
      "managed-by" = "terraform"
    }
  }
}

resource "kubernetes_resource_quota" "app" {
  metadata {
    name      = "taskmanager-quota"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  spec {
    hard = {
      pods            = "20"
      "requests.cpu"  = "4"
      "limits.memory" = "4Gi"
    }
  }
}

resource "kubernetes_config_map" "app" {
  metadata {
    name      = "taskmanager-config"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    FLASK_ENV    = "production"
    DB_HOST      = "postgres"
    DB_NAME      = "taskmanager"
    APP_IMAGE    = var.app_image
    APP_REPLICAS = tostring(var.app_replicas)
  }
}
