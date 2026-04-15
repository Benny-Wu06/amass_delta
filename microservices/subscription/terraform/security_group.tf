resource "aws_security_group" "subscription_lambda_sg" {
  name   = "subscription-lambda-sg"
  vpc_id = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "lambda_sg_id" {
  value = aws_security_group.subscription_lambda_sg.id
}
