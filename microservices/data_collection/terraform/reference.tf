data "archive_file" "reference_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/reference.py"
  output_path = "${path.module}/reference.zip"
}

resource "aws_lambda_function" "reference_scraper" {
  function_name    = "nvd_scrapper"
  role             = aws_iam_role.cisa_role.arn
  handler          = "reference.nvdscrapper"
  runtime          = "python3.12"
  timeout          = 600
  memory_size      = 3000
  filename         = data.archive_file.reference_zip.output_path
  source_code_hash = data.archive_file.reference_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = var.raw_bucket_id
    }
  }
}

resource "aws_cloudwatch_event_target" "run_reference" {
  rule      = aws_cloudwatch_event_rule.twelve_hour_timer.name
  target_id = "nvd_lambda"
  arn       = aws_lambda_function.reference_scraper.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_reference" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reference_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.twelve_hour_timer.arn
}

resource "aws_apigatewayv2_integration" "reference_integration" {
  api_id           = aws_apigatewayv2_api.lambda_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.reference_scraper.invoke_arn
}

resource "aws_apigatewayv2_route" "reference_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "GET /reference"
  target    = "integrations/${aws_apigatewayv2_integration.reference_integration.id}"
}

resource "aws_lambda_permission" "reference_api_gw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.reference_scraper.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/*"
}
