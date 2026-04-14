data "archive_file" "auth_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../"
  output_path = "${path.module}/auth.zip"
  excludes    = ["terraform", "tests", "__pycache__", ".gitignore"]
}

resource "aws_lambda_function" "auth_lambda" {
  filename         = data.archive_file.auth_zip.output_path
  function_name    = "auth-service"
  role             = aws_iam_role.auth_lambda_role.arn
  handler          = "auth_lambda.auth_lambda"
  runtime          = "python3.11"
  timeout          = 30
  source_code_hash = data.archive_file.auth_zip.output_base64sha256

  environment {
    variables = {
      DB_HOST     = var.db_host
      DB_PASSWORD = var.db_password
      DB_NAME     = var.db_name
      DB_USER     = var.db_user
      JWT_SECRET  = var.jwt_secret
    }
  }
}

# Signup
resource "aws_apigatewayv2_route" "auth_signup" {
  api_id    = var.api_id
  route_key = "POST /auth/signup"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# Log in 
resource "aws_apigatewayv2_route" "auth_login" {
  api_id    = var.api_id
  route_key = "POST /auth/login"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# Log out
resource "aws_apigatewayv2_route" "auth_logout" {
  api_id    = var.api_id
  route_key = "POST /auth/logout"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

resource "aws_lambda_permission" "api_gateway_auth" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "auth_integration" {
  api_id                 = var.api_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.auth_lambda.invoke_arn
  payload_format_version = "2.0"
}