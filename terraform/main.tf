provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "cisa_bucket" {
  bucket = "amass-cisa-bucket-01"
}

module "data_collection" {
  source         = "../microservices/data_collection/terraform"
  raw_bucket_arn = aws_s3_bucket.cisa_bucket.arn
  raw_bucket_id  = aws_s3_bucket.cisa_bucket.id

}