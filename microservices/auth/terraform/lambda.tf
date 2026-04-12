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

resource "aws_lambda_permission" "api_gateway_auth" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.auth_api.execution_arn}/*/*"
}