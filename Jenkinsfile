pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        TASKMANAGER_IMAGE = 'taskmanager:ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --disable-pip-version-check -r app/requirements.txt
                '''
            }
        }

        stage('Flake8') {
            steps {
                sh '''
                    . .venv/bin/activate
                    flake8 app --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Pytest') {
            steps {
                sh '''
                    . .venv/bin/activate
                    mkdir -p reports
                    python -m pytest app/tests --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit testResults: 'reports/junit.xml', allowEmptyResults: true
                }
            }
        }

        stage('Docker build') {
            steps {
                sh 'docker build -f docker/Dockerfile -t "$TASKMANAGER_IMAGE" .'
            }
        }

        stage('Archive artifacts') {
            steps {
                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true, fingerprint: true
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true, fingerprint: true
        }
    }
}