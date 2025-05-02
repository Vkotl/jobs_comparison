# SoFi & Galileo job openings changes

Scrapes [SoFi](https://www.sofi.com/careers/), and their subsidiary [Galileo](https://www.galileo-ft.com/careers/), job openings and compares changes over two dates.

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Installation](#installation)
  * [1. Install Docker / Docker Desktop](#1-install-docker--docker-desktop)
  * [2. Install Kubernetes](#2-install-kubernetes)
* [Running the Project](#running-the-project)
  * [1. Pre-building](#1-pre-building)
  * [2. Build Docker Image](#2-build-docker-image)
  * [3. Create Kubernetes Secret](#3-create-kubernetes-secret)
* [Usage](#usage)
* [License](#license)

---

## Overview

This project allows for scraping the open positions on both sites when requested and then allows to compare the positions between two dates. It includes:

* A Python web service, FastAPI.
* A ReactTS frontend.
* A Dockerfile to build a container images for the services.
* Kubernetes manifests (YAML files) to deploy the service in a cluster.

Even if you are not an engineer or familiar with these, you should be able to follow these step-by-step instructions to get the project running on your local computer.

## Features

* **Containerized Python App**: The Python code runs inside a Docker container for consistency.
* **Kubernetes Deployment**: Manage your containers.
* **Easy Setup**: Step-by-step guide for people without experience with these tools.

## Installation
### 1. Install Docker / Docker Desktop

Docker is a tool that "packages" applications into small, self-contained units called containers.\
For installation instruction go to [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

After installation, verify Docker is running:

```bash
docker --version
```

### 2. Install Kubernetes

Kubernetes is a management tool (simplified) for Docker.\
For installation instructions go to [https://kubernetes.io/releases/download/](https://kubernetes.io/releases/download/). If you have Docker Desktop then Kubernetes installation can be done through Docker Desktop settings by enabling Kubernetes.

## Running the Project

Once Docker Desktop is running with Kubernetes enabled, follow these steps.

### 1. Pre-building

Rename `backend/deploy/.env.sample` to `backend/deploy/.env` and open `./backend/deploy/.env` to add the credential you would like to use.

### 2. Build Docker Image

1. Open a terminal in the project directory (where `frontend` and `backend` directories are).

2. Build the Docker images (no local Python install needed):

   ```bash
   docker build -f .\backend\deploy\Dockerfile . --tag=jobsback:latest
   docker build -f .\frontend\Dockerfile . --tag=jobsfront:latest
   ```
   
### 3. Create Kubernetes Secret

Store your backend environment variables securely in a Kubernetes Secret:

```bash
kubectl create secret generic backend-secret --from-env-file=backend/deploy/.env
```

### 3. Deploy to Kubernetes

1. Apply the Kubernetes manifests:

   ```bash
   kubectl apply -f .\k8s\
   ```

2. Verify the deployment:

   ```bash
   kubectl get pods
   kubectl get svc
   ```

3. Access the service:

   Open [http://localhost](http://localhost) in your browser.

## Usage

Once deployed, open your browser to the service URL ([http://localhost](http://localhost)) and you should see the homepage.

## License

This project is licensed under the MIT License.
