variable "aws_region" {
  type        = string
  description = "AWS region for the deployment."
  default     = "ap-northeast-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment name."
  default     = "demo"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR range for the VPC."
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "Two public subnet CIDRs for the ALB."
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Two private subnet CIDRs for ECS and RDS."
  default     = ["10.20.11.0/24", "10.20.12.0/24"]
}

variable "availability_zones" {
  type        = list(string)
  description = "Two availability zones in the selected region."
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "app_image" {
  type        = string
  description = "ECR image URI including an immutable tag such as a commit SHA."
}

variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN for the HTTPS ALB listener."
  default     = null
  nullable    = true
}

variable "db_password" {
  type        = string
  description = "Database password supplied out-of-band (for example TF_VAR_db_password)."
  sensitive   = true
  nullable    = false
}

variable "task_cpu" {
  type        = number
  description = "Fargate task CPU units."
  default     = 256
}

variable "task_memory" {
  type        = number
  description = "Fargate task memory in MiB."
  default     = 512
}
