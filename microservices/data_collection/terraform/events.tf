
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