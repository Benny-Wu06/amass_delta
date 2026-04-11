# role lambda asssumes when it runs 
resource "aws_iam_role" "auth_lambda_role" {
  name = "auth_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# allows lambda write logs to cloudwatch
resource "aws_iam_role_policy_attachment" "auth_lambda_logs" {
  role       = aws_iam_role.auth_lambda_logs.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}