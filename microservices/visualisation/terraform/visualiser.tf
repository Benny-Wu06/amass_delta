data "archive_file" "visualiser_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/visualiser/visualiser_lambda.py"
  output_path = "${path.module}/visualiser.zip"
}

resource "aws_lambda_function" "visualiser_lambda" {
  filename      = data.archive_file.visualiser_zip.output_path
  function_name = "visualisation_graph_generator"
  role          = aws_iam_role.visualisation_role.arn
  handler       = "visualiser_lambda.visualiser_lambda"
  runtime       = "python3.12"
  
  timeout     = 30
  memory_size = 1000 

  layers = [
    "arn:aws:lambda:ap-southeast-2:455322614983:layer:visualiser:1"

  ]

  source_code_hash = data.archive_file.visualiser_zip.output_base64sha256
}

resource "aws_apigatewayv2_integration" "visualiser_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.visualiser_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "visualiser_route" {
  api_id    = var.api_id
  route_key = "POST /v1/visualise" 
  target    = "integrations/${aws_apigatewayv2_integration.visualiser_int.id}"
}

resource "aws_lambda_permission" "visualiser_api_gw_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.visualiser_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}