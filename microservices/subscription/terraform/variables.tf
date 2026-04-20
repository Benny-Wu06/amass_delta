variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "db_address" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "api_id" {
  type = string
}

variable "api_execution_arn" {
  type = string
}

variable "ses_from_email" {
  type = string
}

variable "sns_topic_arn" {
  type        = string
}
