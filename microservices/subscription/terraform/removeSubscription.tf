data "archive_file" "remove_subscription_zip" {
  type        = "zip"
  output_path = "${path.module}/removeSubscription.zip"

  source {
    content  = file("${path.module}/../src/removeSubscription.py")
    filename = "removeSubscription.py"
  }

  source {
    content  = file("${path.module}/../../../global-bundle.pem")
    filename = "global-bundle.pem"
  }
}

resource "aws_lambda_function" "remove_subscription" {
  function_name    = "subscription-remove-company"
  role             = aws_iam_role.subscription_lambda_role.arn
  handler          = "removeSubscription.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.remove_subscription_zip.output_path
  source_code_hash = data.archive_file.remove_subscription_zip.output_base64sha256
  timeout          = 300
  layers = [
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
  ]

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.subscription_lambda_sg.id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_address
      DB_NAME     = var.db_name
      DB_USER     = var.db_user
      DB_PASSWORD = var.db_password
      CERT_PATH   = "global-bundle.pem"
    }
  }
}

resource "aws_apigatewayv2_integration" "remove_subscription_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.remove_subscription.invoke_arn
}

resource "aws_apigatewayv2_route" "remove_subscription_route" {
  api_id    = var.api_id
  route_key = "DELETE /v2/watchlist/{id}/companies/{company_name}"
  target    = "integrations/${aws_apigatewayv2_integration.remove_subscription_int.id}"
}

resource "aws_lambda_permission" "remove_subscription_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remove_subscription.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}
