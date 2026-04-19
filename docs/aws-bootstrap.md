# AWS Bootstrap

This repository now includes:

- `/.github/workflows/ci.yml` for backend checks and extension packaging
- `/.github/workflows/deploy-backend.yml` for backend deployment to AWS ECS/Fargate
- `/infra/terraform` for provisioning the AWS infrastructure

The fastest path now is to use the Terraform stack in `/infra/terraform`.

## 1. Provision the AWS resources with Terraform

Open [infra/terraform/README.md](</C:/Users/ameys/Desktop/Projects/Catch a Phish/infra/terraform/README.md:1>) and follow the two-phase bootstrap flow.

That stack creates:

- a VPC with public subnets
- an Application Load Balancer
- Amazon ECR repository
- GitHub OIDC provider in IAM
- GitHub Actions deploy role
- ECS cluster and supporting IAM/logging resources
- ECS Fargate service, once you enable it after the first image push

## 2. Add GitHub repository variables

From Terraform outputs, add these variables in GitHub repository settings:

- `AWS_REGION`
- `ECR_REPOSITORY`
- `ECS_CLUSTER_NAME`
- `ECS_SERVICE_NAME`

## 3. Add GitHub repository secrets

From Terraform outputs, add these secrets:

- `AWS_ROLE_TO_ASSUME`

Optional future secret for extension release automation:

- `PROD_API_BASE_URL`

Example production API base URL:

- `https://api.catchaphish.com`

## 4. Point the extension build at production

When you are ready to release updated browser extensions, package them with the production API URL:

```powershell
& 'C:\Users\ameys\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\build_extensions.py --api-base-url https://api.catchaphish.com --output-dir dist
```

This produces:

- `dist/catch-a-phish-chrome.zip`
- `dist/catch-a-phish-firefox.zip`

## 5. First deployment checklist

Before pushing to `main`, make sure:

- the Terraform outputs are copied into the matching GitHub variables and secrets
- the ECS service has been enabled in Terraform only after the first image exists in ECR
- the ECS cluster and service names are stored in GitHub only after the service exists
- your production domain points at the ECS load balancer if you plan to use a custom API URL
