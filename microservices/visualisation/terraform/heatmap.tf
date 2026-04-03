data "archive_file" "heatmap_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/heatmap/heatmap_lambda.py"
  output_path = "${path.module}/heatmap.zip"
}

resource "aws_lambda_function" "heatmap_lambda" {
  filename      = data.archive_file.heatmap_zip.output_path
  function_name = "visualisation_heatmap"
  role          = aws_iam_role.visualisation_role.arn
  handler       = "heatmap_lambda.heatmap_lambda"
  runtime       = "python3.12"
  timeout       = 15
  layers = [
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
  ]

  source_code_hash = data.archive_file.heatmap_zip.output_base64sha256

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.visualisation_sg.id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_address
      DB_NAME     = var.db_name
      DB_USER     = var.db_user
      DB_PASSWORD = var.db_password
    }
  }
}

resource "aws_apigatewayv2_integration" "visualisation_heatmap_lambda_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.heatmap_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "heatmap_route" {
  api_id    = var.api_id
  route_key = "GET /v1/heatmap/{company_name}"
  target    = "integrations/${aws_apigatewayv2_integration.visualisation_heatmap_lambda_int.id}"
}

resource "aws_lambda_permission" "visualisation_heatmap_api_gw_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.heatmap_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}