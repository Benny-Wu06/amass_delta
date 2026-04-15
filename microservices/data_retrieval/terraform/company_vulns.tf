data "archive_file" "data_retrieval_zip" {
  type        = "zip"
  output_path = "${path.module}/data_retrieval_zip"

  source {
    content  = file("${path.module}/../src/company_vulnerabilities.py")
    filename = "company_vulnerabilities.py"
  }

  source {
    content  = file("${path.module}/../src/get_all_companies.py")
    filename = "get_all_companies.py"
  }

  source {
    content  = file("${path.module}/../src/global-bundle.pem")
    filename = "global-bundle.pem"
  }
}



#
# IAM Role for Database Access
#
resource "aws_iam_role" "company_vulnerabilities_role" {
  name = "company_vulnerabilities_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}


#
# Allows Lambda to connect to a VPC to reach RDS
#

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.company_vulnerabilities_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "company_vulnerabilities_insights" {
  role       = aws_iam_role.company_vulnerabilities_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}


#
# The Lambda Function
#
resource "aws_lambda_function" "company_vulnerabilities" {
  function_name    = "company_vulnerabilities_service"
  role             = aws_iam_role.company_vulnerabilities_role.arn
  handler          = "company_vulnerabilities.lambda_handler"
  runtime          = "python3.12"
<<<<<<< HEAD
  filename         = data.archive_file.company_vulnerabilities_zip.output_path
  source_code_hash = data.archive_file.company_vulnerabilities_zip.output_base64sha256
=======
  filename         = data.archive_file.data_retrieval_zip.output_path
  source_code_hash = data.archive_file.data_retrieval_zip.output_base64sha256
>>>>>>> 2b92f8fea70cd1e6e3500d0e644f53e8fb449c97
  timeout = 300
  layers  = [
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
# Get all companies lambda
#
resource "aws_lambda_function" "get_all_companies" {
  function_name = "get_all_companies_service"
  
  role          = aws_iam_role.company_vulnerabilities_role.arn
  
  # AWS knows to look for get_all_companies.py inside the shared zip
  handler       = "get_all_companies.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.data_retrieval_zip.output_path
  source_code_hash = data.archive_file.data_retrieval_zip.output_base64sha256
    
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
  }

  layers = [
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1"
  ]

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
resource "aws_apigatewayv2_integration" "company_vulnerabilities_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.company_vulnerabilities.invoke_arn
}

resource "aws_apigatewayv2_route" "company_vulnerabilities_route" {
  api_id    = var.api_id
  route_key = "GET /v1/companies/{company_name}/vulnerabilities"
  target    = "integrations/${aws_apigatewayv2_integration.company_vulnerabilities_int.id}"
}

resource "aws_lambda_permission" "company_vulnerabilities_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.company_vulnerabilities.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}

#
# get_all_companies
#
resource "aws_apigatewayv2_integration" "get_all_companies_int" {
  api_id           = var.api_id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.get_all_companies.invoke_arn
}


resource "aws_apigatewayv2_route" "get_all_companies_route" {
  api_id    = var.api_id
  route_key = "GET /v1/companies"
  target    = "integrations/${aws_apigatewayv2_integration.get_all_companies_int.id}"
}


resource "aws_lambda_permission" "get_all_companies_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_all_companies.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}