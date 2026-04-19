output "aws_region" {
  description = "AWS region used by the infrastructure."
  value       = var.aws_region
}

output "ecr_repository_name" {
  description = "Name of the ECR repository for the backend image."
  value       = aws_ecr_repository.backend.name
}

output "ecr_repository_url" {
  description = "Repository URL to use when pushing the backend image."
  value       = aws_ecr_repository.backend.repository_url
}

output "github_actions_role_arn" {
  description = "IAM role ARN to store as the AWS_ROLE_TO_ASSUME GitHub secret."
  value       = aws_iam_role.github_actions_deploy.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name to store as the ECS_CLUSTER_NAME GitHub variable."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name to store as the ECS_SERVICE_NAME GitHub variable after the service exists."
  value       = try(aws_ecs_service.backend[0].name, null)
}

output "alb_dns_name" {
  description = "Public DNS name assigned to the application load balancer."
  value       = aws_lb.backend.dns_name
}

output "backend_http_base_url" {
  description = "HTTP base URL for the backend before a custom HTTPS domain is added."
  value       = "http://${aws_lb.backend.dns_name}"
}
