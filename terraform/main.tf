provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "cisa_bucket" {
  bucket = "amass-cisa-bucket-01"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "amass-vpc" }
}

resource "aws_subnet" "subnet_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "ap-southeast-2a"
}

resource "aws_subnet" "subnet_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-southeast-2b"
}

resource "aws_db_subnet_group" "main" {
  name       = "vulnerability-db-subnet-group"
  subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
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

  publicly_accessible = false
  skip_final_snapshot = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

module "data_collection" {
  source         = "../microservices/data_collection/terraform"
  vpc_id         = aws_vpc.main.id
  raw_bucket_arn = aws_s3_bucket.cisa_bucket.arn
  raw_bucket_id  = aws_s3_bucket.cisa_bucket.id
  db_name        = aws_db_instance.postgres.db_name
  db_address     = aws_db_instance.postgres.address
  db_user        = aws_db_instance.postgres.username
  db_password    = var.db_password
  bucket_id      = aws_s3_bucket.cisa_bucket.id
  subnet_ids     = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

module "data_retrieval" {
  source         = "../microservices/data_retrieval/terraform"
  private_subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
  lambda_sg_id       = aws_security_group.retrieval_lambda_sg.id
  db_password        = var.db_password
  vpc_id             = aws_vpc.main.id
  db_address         = aws_db_instance.postgres.address
  db_name            = aws_db_instance.postgres.db_name
  db_user            = aws_db_instance.postgres.username
  bucket_id          = aws_s3_bucket.cisa_bucket.id
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.ap-southeast-2.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_vpc.main.main_route_table_id]
}