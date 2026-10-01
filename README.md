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

Copy `.env.example` to `.env` before starting Compose. The `web` service waits for PostgreSQL to pass `pg_isready`; database settings and `DATABASE_URL` are read from `.env`. Open http://localhost:5000. The PostgreSQL data is stored in the `postgres_data` named volume. To stop the services while keeping database data, run:

```powershell
docker compose -f docker/docker-compose.yml down
```

For non-local deployments, replace the example `SECRET_KEY` and database password with securely managed values.

## Run Jenkins CI
Start the Jenkins controller and its isolated Docker builder from the repository root:

```powershell
docker compose -f docker/jenkins/docker-compose.yml up --build -d
```

Open http://localhost:8080. The initial administrator password is available inside the Jenkins container at `/var/jenkins_home/secrets/initialAdminPassword`. Create a Pipeline job from this repository and use the root `Jenkinsfile`; the pipeline installs app requirements in a workspace virtual environment, runs focused Flake8 and pytest/JUnit checks, builds the application image, and archives test reports. Configure the GitHub webhook to target `/github-webhook/` on a Jenkins URL reachable by GitHub to enable push triggers.