FROM python:3.11-slim AS python-runtime

FROM jenkins/jenkins:lts-jdk21

COPY --from=python-runtime /usr/local/ /usr/local/
ENV PATH="/usr/local/bin:${PATH}"

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends docker-cli git && \
    rm -rf /var/lib/apt/lists/*

RUN jenkins-plugin-cli --plugins "workflow-aggregator git github junit workflow-multibranch:842.v3a_b_59b_57b_e6e pipeline-groovy-lib:806.v408277b_33d1d script-security:1422.v06869826dd9b_"

USER jenkins