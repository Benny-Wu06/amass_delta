variable "raw_bucket_arn" {
  type = string
}

variable "raw_bucket_id" {
  type = string
}

variable "vpc_id" {
  type        = string
}

variable "subnet_ids" {
  type        = list(string)
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

variable "db_password" {
  type        = string
  sensitive   = true
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