data "archive_file" "enrichment_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/enrich.py"
  output_path = "${path.module}/enrichment.zip"
}

resource "aws_lambda_function" "enrichment" {
  function_name    = "enrichment"
  role             = aws_iam_role.enrich_role.arn
  handler          = "enrich.enrichment"
  runtime          = "python3.12"
  timeout          = 600
  memory_size      = 3000
  filename         = data.archive_file.enrichment_zip.output_path
  source_code_hash = data.archive_file.enrichment_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = var.raw_bucket_id
    }
  }
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.raw_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.enrichment.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.allow_s3_enricher]
}

resource "aws_apigatewayv2_integration" "enrichment_integration" {
  api_id           = aws_apigatewayv2_api.lambda_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.enrichment.invoke_arn
}

resource "aws_apigatewayv2_route" "enrichment_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "POST /enrichment"
  target    = "integrations/${aws_apigatewayv2_integration.enrichment_integration.id}"
}

resource "aws_lambda_permission" "enrichment_api_gw" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.enrichment.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.lambda_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "allow_s3_enricher" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.enrichment.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.raw_bucket_arn
}