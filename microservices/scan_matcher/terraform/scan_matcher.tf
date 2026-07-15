data "archive_file" "scan_matcher_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/scan_matcher.py"
  output_path = "${path.module}/scan_matcher.zip"
}

resource "aws_lambda_function" "scan_matcher" {
  function_name    = "scan_matcher"
  role             = aws_iam_role.scan_matcher_role.arn
  handler          = "scan_matcher.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  filename         = data.archive_file.scan_matcher_zip.output_path
  source_code_hash = data.archive_file.scan_matcher_zip.output_base64sha256
}

resource "aws_lambda_permission" "scan_matcher_api_gw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scan_matcher.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "scan_matcher_integration" {
  api_id                 = var.api_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.scan_matcher.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "scan_matcher_route" {
  api_id    = var.api_id
  route_key = "POST /v1/scan/match"
  target    = "integrations/${aws_apigatewayv2_integration.scan_matcher_integration.id}"
}
