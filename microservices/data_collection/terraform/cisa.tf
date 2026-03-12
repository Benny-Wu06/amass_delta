data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/cisa.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "cisa_scraper" {
  function_name    = "cisa_scraper"
  role             = aws_iam_role.cisa_role.arn
  handler          = "cisa.cisascrapper"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = var.raw_bucket_id
    }
  }
}
