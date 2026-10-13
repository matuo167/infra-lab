terraform {
  required_version = ">= 1.6.0, < 2.0.0"

  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "infra-lab"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}
