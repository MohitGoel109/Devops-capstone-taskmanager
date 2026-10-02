# Progress

- Stage 1: Docker completed in the repo baseline (compose with Postgres, health-check, local app startup). Verified earlier in this codebase.
- Stage 2: Jenkins CI bootstrap in progress on branch feature/jenkins-ci.
- Stage 2 issue found: Jenkins is using Python 3.13 and the earlier dependency pin `greenlet==3.0.3` does not build there. The Jenkins image also lacked C/C++ build tools (`g++`), which caused the compile failure. Root cause confirmed: `greenlet==3.1.4` was invalid and does not exist in the package index; the correct fix is to use a published Python 3.13-compatible release such as `greenlet==3.1.1` alongside the build tooling install.
- Stage 2 final issue found: the Jenkins runtime container had no `docker` CLI on PATH, so the Docker build stage failed with `docker: not found`. Fix: install `docker.io` and expose `/usr/bin/docker` via symlink so the Jenkins pipeline can call Docker.
