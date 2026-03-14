# provider "aws" {
#   region = "ap-southeast-2"
# }

# IAM role for Lambda execution
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "vuln_info_role" {
  name               = "vuln_info_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Package the Lambda function code
data "archive_file" "vuln_info_archive" {
  type        = "zip"
  source_dir = "${path.module}/../src/vuln_info_package"
  output_path = "${path.module}/vuln_info_lambda.zip"
}

# Lambda function
resource "aws_lambda_function" "vuln_info_lambda" {
  filename      = data.archive_file.vuln_info_archive.output_path
  function_name = "vuln_info_lambda"
  role          = aws_iam_role.vuln_info_role.arn
  handler       = "vulnerability_info.lambda_handler"
  code_sha256   = data.archive_file.example.output_base64sha256

  runtime = "python3.12"

  environment {
    variables = {
      ENVIRONMENT = "dev"
      LOG_LEVEL   = "info"
    }
  }

  tags = {
    Environment = "dev"
    Application = "vuln_info"
  }
}