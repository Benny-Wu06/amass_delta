data "archive_file" "db_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../package" 
  output_path = "${path.module}/db_retrieval.zip"
}