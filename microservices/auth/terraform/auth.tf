data "archive_file" "auth_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../"
  output_path = "${path.module}/auth.zip"
  excludes    = ["terraform", "tests", "__pycache__", ".gitignore"]
}

resource "aws_security_group" "auth_sg" {
  name   = "auth-lambda-sg"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "auth_role" {
  name = "auth_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.auth_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_lambda_function" "auth_lambda" {
  filename         = data.archive_file.auth_zip.output_path
  function_name    = "auth-service"
  role             = aws_iam_role.auth_role.arn
  handler          = "auth_lambda.auth_lambda"
  runtime          = "python3.12"
  timeout          = 30
  source_code_hash = data.archive_file.auth_zip.output_base64sha256

  layers = [
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-requests:23",
    "arn:aws:lambda:ap-southeast-2:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64"
  ]

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.auth_sg.id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_address
      DB_PASSWORD = var.db_password
      DB_NAME     = var.db_name
      DB_USER     = var.db_user
      # JWT_SECRET  = var.jwt_secret
    }
  }
}

resource "aws_apigatewayv2_integration" "auth_integration" {
  api_id                 = var.api_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.auth_lambda.invoke_arn
  payload_format_version = "2.0"
}

# Signup
resource "aws_apigatewayv2_route" "auth_signup" {
  api_id    = var.api_id
  route_key = "POST /auth/signup"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# Log in 
resource "aws_apigatewayv2_route" "auth_login" {
  api_id    = var.api_id
  route_key = "POST /auth/login"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# Log out
resource "aws_apigatewayv2_route" "auth_logout" {
  api_id    = var.api_id
  route_key = "POST /auth/logout"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

resource "aws_lambda_permission" "api_gateway_auth" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.auth_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}
