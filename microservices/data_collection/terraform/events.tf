
resource "aws_cloudwatch_event_rule" "twelve_hour_timer" {
  name                = "cisa-twelve-hour-timer"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "run_scraper" {
  rule      = aws_cloudwatch_event_rule.twelve_hour_timer.name
  target_id = "lambda"
  arn       = aws_lambda_function.cisa_scraper.arn
}

