data "archive_file" "get_all_cves_zip" {
  type        = "zip"
  output_path = "${path.module}/get_all_cves.zip"

  source {
    content  = file("${path.module}/../src/get_all_cves.py")
    filename = "get_all_cves.py"
  }

  source {
    content  = file("${path.module}/../src/global-bundle.pem")
    filename = "global-bundle.pem"
  }
}

#
# The Lambda Function
#
resource "aws_lambda_function" "get_all_cves" {
  function_name    = "get_all_cves_service"
  role             = aws_iam_role.company_vulnerabilities_role.arn
  handler          = "get_all_cves.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.get_all_cves_zip.output_path
  source_code_hash = data.archive_file.get_all_cves_zip.output_base64sha256
  timeout          = 300
  
  layers = [
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
  ]

  # Networking: Must match your RDS VPC
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
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

#
#  API Gateway Integration
#
resource "aws_apigatewayv2_integration" "get_all_cves_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_all_cves.invoke_arn
}

resource "aws_apigatewayv2_route" "get_all_cves_route" {
  api_id    = var.api_id
  route_key = "GET /v1/cves"
  target    = "integrations/${aws_apigatewayv2_integration.get_all_cves_int.id}"
}


resource "aws_lambda_permission" "get_all_cves_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_all_cves.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}