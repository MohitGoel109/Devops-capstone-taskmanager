# DevOps Capstone: Task Manager

End-to-end DevOps pipeline for deploying a cloud-native Task Manager application.

## Tools
Git, GitHub, Jenkins, Docker, Kubernetes, Ansible, Terraform, Prometheus, Grafana, ArgoCD

## Folder Structure
- app/ : application source code
- docker/ : Dockerfile and docker-compose
- jenkins/ : Jenkinsfile
- k8s/ : Kubernetes manifests
- ansible/ : playbooks
- terraform/ : infrastructure code
- monitoring/ : Prometheus and Grafana configs
- docs/ : report, diagrams, screenshots

## Run with Docker Compose
From the repository root, build and start the task manager:

```powershell
docker compose -f docker/docker-compose.yml up --build -d
```

Open http://localhost:5000. The container health check uses `/health`, and task data is stored in the `taskmanager_data` named volume. To stop the service while keeping its data, run:

```powershell
docker compose -f docker/docker-compose.yml down
```

For non-local deployments, set `SECRET_KEY` in the environment before starting Compose.