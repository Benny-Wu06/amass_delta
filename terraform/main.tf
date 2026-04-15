provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "cisa_bucket" {
  bucket = "amass-cisa-bucket-${var.aws_suffix}"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "amass-vpc" }
}

resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-southeast-2a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "ap-southeast-2b"
  map_public_ip_on_launch = true
}

resource "aws_db_subnet_group" "main" {
  name       = "vulnerability-db-subnet-group"
  subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

# internet gateway for accessing db
resource "aws_internet_gateway" "amass_igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "amass-igw" }
}

# route table for accessing db
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0" #public
    gateway_id = aws_internet_gateway.amass_igw.id
  }

  tags = { Name = "amass-public-rt" }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_security_group" "rds_sg" {
  name   = "vulnerability-db-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.retrieval_lambda_sg.id]
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # allows for public access from any kind of traffic
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.data_collection.lambda_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "retrieval_lambda_sg" {
  name   = "retrieval-lambda-sg"
  vpc_id = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier        = "amass-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "postgres"
  username          = "postgres"

  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  publicly_accessible = true
  skip_final_snapshot = true

  # don't setup db until igw is attached to vpc
  depends_on = [
    aws_internet_gateway.amass_igw
  ]
}

variable "db_password" {
  type      = string
  sensitive = true
}

output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

resource "aws_apigatewayv2_api" "unified_api" {
  name          = "amass-unified-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "OPTIONS", "POST", "PUT", "DELETE"]
    allow_headers = ["*"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_stage" "unified_stage" {
  api_id      = aws_apigatewayv2_api.unified_api.id
  name        = "$default"
  auto_deploy = true
}

output "api_url" {
  value = aws_apigatewayv2_api.unified_api.api_endpoint
}

module "data_collection" {
  source            = "../microservices/data_collection/terraform"
  vpc_id            = aws_vpc.main.id
  raw_bucket_arn    = aws_s3_bucket.cisa_bucket.arn
  raw_bucket_id     = aws_s3_bucket.cisa_bucket.id
  db_name           = aws_db_instance.postgres.db_name
  db_address        = aws_db_instance.postgres.address
  db_user           = aws_db_instance.postgres.username
  db_password       = var.db_password
  bucket_id         = aws_s3_bucket.cisa_bucket.id
  subnet_ids        = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
  api_id            = aws_apigatewayv2_api.unified_api.id
  api_execution_arn = aws_apigatewayv2_api.unified_api.execution_arn
}

module "data_retrieval" {
  source             = "../microservices/data_retrieval/terraform"
  private_subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
  lambda_sg_id       = aws_security_group.retrieval_lambda_sg.id
  db_password        = var.db_password
  vpc_id             = aws_vpc.main.id
  db_address         = aws_db_instance.postgres.address
  db_name            = aws_db_instance.postgres.db_name
  db_user            = aws_db_instance.postgres.username
  bucket_id          = aws_s3_bucket.cisa_bucket.id
  api_id             = aws_apigatewayv2_api.unified_api.id
  api_execution_arn  = aws_apigatewayv2_api.unified_api.execution_arn
}

module "visualisation" {
  source            = "../microservices/visualisation/terraform"
  subnet_ids        = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
  db_password       = var.db_password
  vpc_id            = aws_vpc.main.id
  db_address        = aws_db_instance.postgres.address
  db_name           = aws_db_instance.postgres.db_name
  db_user           = aws_db_instance.postgres.username
  api_id            = aws_apigatewayv2_api.unified_api.id
  api_execution_arn = aws_apigatewayv2_api.unified_api.execution_arn
}

module "integration" {
  source            = "../microservices/integration/terraform"
  vpc_id            = aws_vpc.main.id
  subnet_ids        = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
  db_address        = aws_db_instance.postgres.address
  db_name           = aws_db_instance.postgres.db_name
  db_user           = aws_db_instance.postgres.username
  db_password       = var.db_password
  charlie_email     = var.charlie_email
  charlie_password  = var.charlie_password
  api_id            = aws_apigatewayv2_api.unified_api.id
  api_execution_arn = aws_apigatewayv2_api.unified_api.execution_arn
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.ap-southeast-2.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = [
    aws_vpc.main.main_route_table_id,
    aws_route_table.public_rt.id,
  ]
}

terraform {
  backend "s3" {}
}