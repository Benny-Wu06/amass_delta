variable "db_host" {
  description = "PostgreSQL database host"
}

variable "db_password" {
  description = "PostgreSQL database password"
  sensitive   = true
}

variable "db_name" {
  default = "postgres"
}

variable "db_user" {
  default = "postgres"
}

variable "jwt_secret" {
  description = "Secret key for signing JWT tokens"
  sensitive   = true
}

variable "api_id" {
  type = string
}

variable "api_execution_arn" {
  type = string
}