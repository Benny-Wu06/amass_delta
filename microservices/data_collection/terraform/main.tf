provider "aws" {
  region = "ap-southeast-2"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/cisa.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_iam_role" "cisa_role" {
  name = "cisa_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "CisaLambda"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "s3_access" {
  name = "s3_write_permission"
  role = aws_iam_role.cisa_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${var.raw_bucket_arn}/*"
      }
    ]
  })
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

resource "aws_cloudwatch_event_rule" "twelve_hour_timer" {
  name                = "cisa-twelve-hour-timer"
  schedule_expression = "rate(12 hours)"
}

resource "aws_cloudwatch_event_target" "run_scraper" {
  rule      = aws_cloudwatch_event_rule.twelve_hour_timer.name
  target_id = "lambda"
  arn       = aws_lambda_function.cisa_scraper.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cisa_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.twelve_hour_timer.arn
}

resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "cisa-scraper-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "api_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.lambda_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.cisa_scraper.invoke_arn
}

resource "aws_apigatewayv2_route" "scrape_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "GET /scrape"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "api_gw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cisa_scraper.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/*"
}