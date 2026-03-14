#
#  Package the Lambda function along with its dependencies (psycopg2)
#
data "archive_file" "db_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../microservices/data_retrieval/package" 
  output_path = "${path.module}/db_retrieval.zip"
}


#
# IAM Role for Database Access
#
resource "aws_iam_role" "db_retrieval_role" {
  name = "db_retrieval_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}


#
# Allows Lambda to connect to a VPC to reach RDS
#

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.db_retrieval_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}


#
# The Lambda Function
#
resource "aws_lambda_function" "db_retrieval" {
  function_name    = "db_retrieval_service"
  role             = aws_iam_role.db_retrieval_role.arn
  handler          = "company_vulnerabilities.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.db_lambda_zip.output_path
  source_code_hash = data.archive_file.db_lambda_zip.output_base64sha256

  # Networking: Must match your RDS VPC
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
  }

  environment {
    variables = {
      DB_HOST     = "testdb.cby62qewyxsr.ap-southeast-2.rds.amazonaws.com"
      DB_PASSWORD = var.db_password
      CERT_PATH   = "global-bundle.pem"
    }
  }
}


#
#  API Gateway (HTTP API)
#
resource "aws_apigatewayv2_api" "db_api" {
  name          = "db-retrieval-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "db_api_stage" {
  api_id      = aws_apigatewayv2_api.db_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "db_lambda_int" {
  api_id           = aws_apigatewayv2_api.db_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.db_retrieval.invoke_arn
}

resource "aws_apigatewayv2_route" "db_route" {
  api_id    = aws_apigatewayv2_api.db_api.id
  route_key = "GET /v1/companies/{company_name}/vulnerabilities"
  target    = "integrations/${aws_apigatewayv2_integration.db_lambda_int.id}"
}

resource "aws_lambda_permission" "db_api_gw_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.db_retrieval.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.db_api.execution_arn}/*/*"
}

#
# Outputs
#
output "api_base_url" {
  description = "The base URL for the API Gateway"
  value       = aws_apigatewayv2_api.db_api.api_endpoint
}

output "vulnerability_endpoint" {
  description = "The specific endpoint for company vulnerabilities"
  value       = "${aws_apigatewayv2_api.db_api.api_endpoint}/v1/companies/{company_name}/vulnerabilities"
}