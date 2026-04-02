data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/cisa.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "cisa_scraper" {
  function_name    = "cisa_scraper"
  role             = aws_iam_role.cisa_role.arn
  handler          = "cisa.cisascrapper"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = var.raw_bucket_id
    }
  }
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cisa_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.twelve_hour_timer.arn
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.cisa_scraper.invoke_arn
}

resource "aws_apigatewayv2_route" "scrape_route" {
  api_id    = var.api_id
  route_key = "GET /scrape"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "api_gw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cisa_scraper.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}

