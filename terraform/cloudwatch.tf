resource "aws_cloudwatch_log_group" "cisa_scraper" {
  name              = "/aws/lambda/cisa_scraper"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "nvd_scrapper" {
  name              = "/aws/lambda/nvd_scrapper"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "enrichment" {
  name              = "/aws/lambda/enrichment"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "amass_rds_processor" {
  name              = "/aws/lambda/amass-rds-processor"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "company_vulnerabilities_service" {
  name              = "/aws/lambda/company_vulnerabilities_service"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "company_summary_lambda" {
  name              = "/aws/lambda/company_summary_lambda"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "vuln_info_lambda" {
  name              = "/aws/lambda/vuln_info_lambda"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "cve_growth_visualiser" {
  name              = "/aws/lambda/cve-growth-visualiser"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "visualisation_heatmap" {
  name              = "/aws/lambda/visualisation_heatmap"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "visualisation_graph_generator" {
  name              = "/aws/lambda/visualisation_graph_generator"
  retention_in_days = 30
}
