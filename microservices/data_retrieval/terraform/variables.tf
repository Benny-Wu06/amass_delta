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
  sensitive   = true # This hides the password from your console logs
}