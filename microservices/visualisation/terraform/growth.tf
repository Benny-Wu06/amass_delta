data "archive_file" "growth_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/cve_growth/cve_growth_lambda.py"
  output_path = "${path.module}/cve_growth_lambda.zip"
}

resource "aws_security_group" "visualisation_sg" {
  name   = "amass-processor-sg-2"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "visualisation_role" {
  name = "visualisation_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "processor_policy" {
  role = aws_iam_role.visualisation_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "vpc_execution" {
  role       = aws_iam_role.visualisation_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

output "lambda_sg_id" {
  value = aws_security_group.visualisation_sg.id
}

resource "aws_lambda_function" "visualisation_lambda" {
  filename      = data.archive_file.growth_zip.output_path
  function_name = "cve-growth-visualiser"
  role          = aws_iam_role.visualisation_role.arn
  handler       = "cve_growth_lambda.cve_growth_lambda"
  runtime       = "python3.12"
  timeout       = 15
  layers = ["arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1"]

  source_code_hash = data.archive_file.growth_zip.output_base64sha256

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

resource "aws_apigatewayv2_api" "visualisation_api" {
  name          = "cve-growth-visualisation-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "visualisation_api_stage" {
  api_id      = aws_apigatewayv2_api.visualisation_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "visualisation_lambda_int" {
  api_id           = aws_apigatewayv2_api.visualisation_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.visualisation_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "visualisation_route" {
  api_id    = aws_apigatewayv2_api.visualisation_api.id
  route_key = "GET /v1/growth/{company_name}"
  target    = "integrations/${aws_apigatewayv2_integration.visualisation_lambda_int.id}"
}

resource "aws_lambda_permission" "visualisation_api_gw_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.visualisation_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.visualisation_api.execution_arn}/*/*"
}