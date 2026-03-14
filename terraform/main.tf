provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "cisa_bucket" {
  bucket = "amass-cisa-bucket-01"
}

module "data_collection" {
  source         = "../microservices/data_collection/terraform"
  raw_bucket_arn = aws_s3_bucket.cisa_bucket.arn
  raw_bucket_id  = aws_s3_bucket.cisa_bucket.id

}





resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "amass-vpc" }
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
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier           = "amass-db"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "postgres"
  username             = "postgres"
  
  password             = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  
  publicly_accessible = false
  skip_final_snapshot = true
}

variable "db_password" {
  type        = string
  sensitive   = true
}

output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}