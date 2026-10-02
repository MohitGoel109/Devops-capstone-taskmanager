# Jenkins setup

1. Start Jenkins: `docker compose -f docker/jenkins/docker-compose.yml up -d --build`
2. Get the initial admin password: `docker exec -it <jenkins-container> sh -lc 'cat /var/jenkins_home/secrets/initialAdminPassword'`
3. Open `http://localhost:8080` in the browser.
4. Unlock Jenkins with the password from step 2.
5. Install suggested plugins, then create the first admin user.
6. Create a new Pipeline job.
7. Choose `Pipeline script from SCM`.
8. Set Repository URL to your GitHub repo, branch to `develop` or your feature branch, and Script Path to `jenkins/Jenkinsfile`.
9. Enable `GitHub hook trigger for GITScm polling`.
10. For GitHub webhook testing: run `ngrok http 8080`, then add a webhook at `https://<ngrok-url>/github-webhook/` with `application/json` and push events.

This setup verifies the Jenkins pipeline can run from source control and auto-trigger on GitHub pushes.
