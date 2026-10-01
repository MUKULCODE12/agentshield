# AWS Infrastructure-as-Code (Terraform) for Sentinel / AgentShield
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

# 1. Amazon ECR Container Repositories
resource "aws_ecr_repository" "backend_repo" {
  name                 = "agentshield-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "frontend_repo" {
  name                 = "agentshield-frontend"
  image_tag_mutability = "MUTABLE"
}

# 2. Amazon S3 Bucket for Audit Reports & PDFs
resource "aws_s3_bucket" "audit_reports_bucket" {
  bucket        = "agentshield-audit-reports-prod"
  force_destroy = true
}

# 3. AWS Secrets Manager for API Keys
resource "aws_secretsmanager_secret" "agentshield_secrets" {
  name = "agentshield/prod/api_keys"
}

resource "aws_secretsmanager_secret_version" "agentshield_secrets_val" {
  secret_id     = aws_secretsmanager_secret.agentshield_secrets.id
  secret_string = jsonencode({
    SECRET_KEY     = "super_secret_jwt_key_prod"
    OPENAI_API_KEY = "sk-proj-demo"
  })
}

# 4. Amazon RDS PostgreSQL Database
resource "aws_db_instance" "postgres_rds" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t4g.micro"
  db_name              = "agentshield_db"
  username             = "agentshield_admin"
  password             = "SecureRDSSecret2026!"
  skip_final_snapshot  = true
  publicly_accessible  = false
}

# 5. AWS ECS Cluster & Fargate Service
resource "aws_ecs_cluster" "sentinel_cluster" {
  name = "sentinel-agentshield-cluster"
}

resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/agentshield"
  retention_in_days = 30
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend_task" {
  family                   = "agentshield-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/agentshield"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])
}

# IAM Role for ECS Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "agentshield_ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

output "ecr_backend_url" {
  value = aws_ecr_repository.backend_repo.repository_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.audit_reports_bucket.bucket
}
