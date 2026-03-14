# create lambda function
data "archive_file" "vuln_info_zip" {
  type = "zip"
  source_file = "../src/vulnerability_info.py"
  output_path = "vulnerability_info.zip"
}

provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_iam_role" "vuln_info_role" {
  name = "vuln_info_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "vuln_info_lambda"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
  
}

resource "aws_iam_role_policy" "vuln_info_role_attachment" {
  name = "execute_vuln_info"
  role = aws_iam_role.vuln_info_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${var.raw_bucket_arn}/*"
      }
    ]
  })
}

