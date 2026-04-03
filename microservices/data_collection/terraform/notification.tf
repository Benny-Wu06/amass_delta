resource "aws_s3_bucket_notification" "s3_trigger" {
  bucket = var.raw_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.enrichment.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/"
    filter_suffix       = ".json"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.data_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "enriched/"
    filter_suffix       = ".json"
  }

  depends_on = [
    aws_lambda_permission.allow_s3_enricher,
    aws_lambda_permission.allow_s3_processor
  ]
}