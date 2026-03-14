data "archive_file" "db_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../package" 
  output_path = "${path.module}/db_retrieval.zip"
}

resource "aws_iam_role" "company_summary_role" {
  name = "company_summary_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.company_summary_role
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_lambda_function" "company_summary" {
  function_name    = "company_summary_lambda"
  role             = aws_iam_role.company_summary_role.arn
  handler          = "company_summary.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.db_lambda_zip.output_path
  source_code_hash = data.archive_file.db_lambda_zip.output_base64sha256
  layers = ["arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1"]


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

# integrate lambda to api gateway
resource "aws_apigatewayv2_integration" "company_summary_db_integration" {
  api_id             = aws_apigatewayv2_api.db_api.id 
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.company_summary.invoke_arn
  integration_method = "POST" 
}

resource "aws_apigatewayv2_route" "company_summary_route" {
  api_id    = aws_apigatewayv2_api.db_api.id
  route_key = "GET /v1/companies/{company_name}"
  target    = "integrations/${aws_apigatewayv2_integration.company_summary_db_integration.id}"
}

resource "aws_lambda_permission" "apigw_lambda_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.company_summary.function_name
  principal     = "apigateway.amazonaws.com"

  # uses the execution arn of the API defined in main.tf
  source_arn = "${aws_apigatewayv2_api.db_api.execution_arn}/*/*" 
}

output "company_summary_endpoint" {
  description = "The specific endpoint for getting a company summary"
  value       = "${aws_apigatewayv2_api.db_api.api_endpoint}/v1/companies/{company_name}"
}