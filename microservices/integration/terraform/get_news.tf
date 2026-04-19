data "archive_file" "get_news_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/get_news_lambda.py"
  output_path = "${path.module}/get_news.zip"
}

resource "aws_lambda_function" "get_news_lambda" {
  filename      = data.archive_file.get_news_zip.output_path
  function_name = "integration_get_news"
  role          = aws_iam_role.integration_role.arn
  handler       = "get_news_lambda.get_news_lambda"
  runtime       = "python3.12"
  timeout       = 30

  layers = [
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-requests:23"
  ]

  source_code_hash = data.archive_file.get_news_zip.output_base64sha256

  environment {
    variables = {
      DB_HOST          = var.db_address
      DB_NAME          = var.db_name
      DB_USER          = var.db_user
      DB_PASSWORD      = var.db_password
    }
  }
}

resource "aws_apigatewayv2_integration" "get_news_lambda_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_news_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "get_news_route" {
  api_id    = var.api_id
  route_key = "GET /v1/news/{company_symbol}"
  target    = "integrations/${aws_apigatewayv2_integration.get_news_lambda_int.id}"
}

resource "aws_lambda_permission" "get_news_api_gw_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_news_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}