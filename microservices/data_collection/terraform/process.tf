data "archive_file" "processor_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/processor.py"
  output_path = "${path.module}/processor.zip"
}

resource "aws_lambda_function" "data_processor" {
  function_name    = "amass-rds-processor"
  role             = aws_iam_role.processor_role.arn
  handler          = "processor.lambda_handler"
  runtime          = "python3.12"
  timeout          = 300
  filename         = data.archive_file.processor_zip.output_path
  source_code_hash = data.archive_file.processor_zip.output_base64sha256
  layers = ["arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1"]

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.lambda_processor_sg.id]
  }

  environment {
    variables = {
    DB_HOST     = var.db_address
    DB_NAME     = var.db_name
    DB_USER     = var.db_user
    DB_PASSWORD = var.db_password
    BUCKET_NAME = var.raw_bucket_id
        }
    }
}

resource "aws_security_group" "lambda_processor_sg" {
  name   = "amass-processor-sg"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "processor_role" {
  name = "processor_role"

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
  role = aws_iam_role.processor_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = ["${var.raw_bucket_arn}/*", "${var.raw_bucket_arn}"]
      },
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

output "lambda_sg_id" {
  value = aws_security_group.lambda_processor_sg.id
}

resource "aws_lambda_permission" "allow_s3_processor" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.raw_bucket_arn
}

resource "aws_s3_bucket_notification" "processor_notification" {
  bucket = var.raw_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.data_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "enriched/"
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.allow_s3_processor]
}
