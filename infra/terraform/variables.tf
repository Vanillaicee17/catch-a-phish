variable "aws_region" {
  description = "AWS region where the infrastructure will be created."
  type        = string
  default     = "ap-south-1"
}

variable "app_name" {
  description = "Base name used for the AWS resources."
  type        = string
  default     = "catch-a-phish"
}

variable "github_owner" {
  description = "GitHub user or organization that owns this repository."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository name."
  type        = string
}

variable "github_branch" {
  description = "Git branch allowed to assume the GitHub Actions deployment role."
  type        = string
  default     = "main"
}

variable "github_oidc_thumbprint" {
  description = "Thumbprint for the GitHub Actions OIDC provider. Override only if GitHub rotates certificates."
  type        = string
  default     = "6938fd4d98bab03faadb97b34396831e3780aea1"
}

variable "vpc_cidr" {
  description = "CIDR block for the application VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "ecr_repository_name" {
  description = "Name of the private ECR repository that stores the backend container image."
  type        = string
  default     = "catch-a-phish-backend"
}

variable "ecr_force_delete" {
  description = "Whether Terraform should delete the ECR repository even if it still contains images."
  type        = bool
  default     = false
}

variable "ecr_image_retention_count" {
  description = "How many images to keep in ECR before older ones are expired."
  type        = number
  default     = 30
}

variable "enable_ecs_service" {
  description = "Set to true after the first image has been pushed to ECR, so Terraform can create the ECS service."
  type        = bool
  default     = false
}

variable "ecs_service_name" {
  description = "Name of the ECS service."
  type        = string
  default     = "catch-a-phish-service"
}

variable "ecs_image_tag" {
  description = "Container image tag the ECS task definition should reference."
  type        = string
  default     = "latest"
}

variable "ecs_desired_count" {
  description = "Desired number of Fargate tasks for the ECS service."
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Task CPU units for Fargate."
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "Task memory in MiB for Fargate."
  type        = number
  default     = 2048
}

variable "container_port" {
  description = "Port exposed by the application container."
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "HTTP health check path used by the ALB target group."
  type        = string
  default     = "/health"
}

variable "log_retention_in_days" {
  description = "Retention period for ECS application logs in CloudWatch."
  type        = number
  default     = 14
}

variable "ecs_environment_variables" {
  description = "Environment variables injected into the ECS task definition."
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Extra tags applied to supported AWS resources."
  type        = map(string)
  default     = {}
}
