terraform {
  backend "s3" {
    bucket = "amass-bucket-github"
    key    = "seng3011/terraform.tfstate"
    region = "ap-southeast-2"
  }
}