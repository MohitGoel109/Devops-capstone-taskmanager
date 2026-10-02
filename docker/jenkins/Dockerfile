FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        docker.io \
        git \
        python3 \
        python3-pip \
        python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN jenkins-plugin-cli --plugins "git github pipeline-stage-view workflow-aggregator junit pipeline-groovy-lib" 

USER jenkins