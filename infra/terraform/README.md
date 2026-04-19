# Terraform Infrastructure

This Terraform stack provisions the AWS resources needed for an ECS/Fargate deployment:

- VPC with two public subnets
- Internet gateway and public routing
- Application Load Balancer
- Amazon ECR repository for the Rust backend image
- ECS cluster
- CloudWatch log group
- ECS task execution and task roles
- GitHub OIDC provider and GitHub Actions deploy role
- Optional ECS Fargate service

## Why the ECS service is optional at first

The bootstrap flow is cleaner if the first container image exists in ECR before Terraform tries to start the ECS service.

That means the recommended flow is:

1. Apply Terraform with `enable_ecs_service = false`
2. Configure GitHub with the Terraform outputs
3. Push the first backend image to ECR using the GitHub Actions workflow
4. Set `enable_ecs_service = true`
5. Apply Terraform again to create the ECS Fargate service
6. Add the ECS cluster and service names to GitHub so deployments can trigger rolling updates

## Usage

```powershell
cd infra\terraform
copy terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## First apply

For the first apply, keep:

```hcl
enable_ecs_service = false
```

Then take these Terraform outputs and add them to GitHub:

- `aws_region` -> repository variable `AWS_REGION`
- `ecr_repository_name` -> repository variable `ECR_REPOSITORY`
- `github_actions_role_arn` -> repository secret `AWS_ROLE_TO_ASSUME`

At this point, the deploy workflow can push images to ECR even though the ECS service does not exist yet.

## Second apply

After the backend image has been pushed to ECR with the `latest` tag, update `terraform.tfvars`:

```hcl
enable_ecs_service = true
```

Apply again:

```powershell
terraform apply
```

Then store these outputs in GitHub:

- `ecs_cluster_name` -> repository variable `ECS_CLUSTER_NAME`
- `ecs_service_name` -> repository variable `ECS_SERVICE_NAME`

From that point on, the deploy workflow will both push the image and trigger a new ECS deployment.

## Important note about HTTPS

This stack creates a public Application Load Balancer with HTTP on port 80.

That is enough for smoke testing and internal validation, but your browser extensions should eventually call an HTTPS API endpoint. The next step after the ECS service is healthy should be adding:

- an ACM certificate
- a Route 53 record such as `api.catchaphish.com`
- an HTTPS listener on the load balancer
