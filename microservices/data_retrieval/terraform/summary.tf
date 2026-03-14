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