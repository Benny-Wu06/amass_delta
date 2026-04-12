variable "private_subnet_ids" {
  description = "List of VPC subnet IDs where the Lambda should run"
  type        = list(string)
}

variable "lambda_sg_id" {
  description = "The security group ID for the Lambda function"
  type        = string
}

variable "db_password" {
  description = "The password for the RDS instance"
  type        = string
  sensitive   = true # this hides the password in console logs
}

variable "vpc_id" {
  type        = string
}

variable "db_address" {
  type        = string
}

variable "db_name" {
  type        = string
}

variable "db_user" {
  type        = string
}

variable "bucket_id" {
  type        = string
}

variable "api_id" {
  type = string
}

variable "api_execution_arn" {
  type = string
}