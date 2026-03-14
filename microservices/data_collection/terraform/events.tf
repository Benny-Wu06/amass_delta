
resource "aws_cloudwatch_event_rule" "twelve_hour_timer" {
  name                = "cisa-twelve-hour-timer"
  schedule_expression = "rate(12 hours)"
}

resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "cisa-scraper-api"
  protocol_type = "HTTP"
}

resource "aws_cloudwatch_event_target" "run_scraper" {
  rule      = aws_cloudwatch_event_rule.twelve_hour_timer.name
  target_id = "lambda"
  arn       = aws_lambda_function.cisa_scraper.arn
}

resource "aws_apigatewayv2_stage" "api_stage" {
  api_id      = aws_apigatewayv2_api.lambda_api.id
  name        = "$default"
  auto_deploy = true
}
