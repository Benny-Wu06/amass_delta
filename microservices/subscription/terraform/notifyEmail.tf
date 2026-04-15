data "archive_file" "notify_email_zip" {
  type        = "zip"
  output_path = "${path.module}/notifyEmail.zip"

  source {
    content  = file("${path.module}/../src/notifyEmail.py")
    filename = "notifyEmail.py"
  }

  source {
    content  = file("${path.module}/../../../global-bundle.pem")
    filename = "global-bundle.pem"
  }
}

resource "aws_iam_role" "notify_email_role" {
  name = "subscription_notify_email_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "notify_email_vpc_access" {
  role       = aws_iam_role.notify_email_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "notify_email_insights" {
  role       = aws_iam_role.notify_email_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role_policy" "notify_email_ses_policy" {
  name = "subscription_notify_email_ses"
  role = aws_iam_role.notify_email_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "ses:SendEmail"
      Resource = "*"
    }]
  })
}

resource "aws_lambda_function" "notify_email" {
  function_name    = "subscription-notify-email"
  role             = aws_iam_role.notify_email_role.arn
  handler          = "notifyEmail.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.notify_email_zip.output_path
  source_code_hash = data.archive_file.notify_email_zip.output_base64sha256
  timeout          = 300
  layers = [
    "arn:aws:lambda:ap-southeast-2:580247275435:layer:LambdaInsightsExtension:21",
    "arn:aws:lambda:ap-southeast-2:770693421928:layer:Klayers-p312-psycopg2-binary:1",
  ]

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.subscription_lambda_sg.id]
  }

  environment {
    variables = {
      DB_HOST     = var.db_address
      DB_NAME     = var.db_name
      DB_USER     = var.db_user
      DB_PASSWORD = var.db_password
      CERT_PATH   = "global-bundle.pem"
      FROM_EMAIL  = var.ses_from_email
    }
  }
}

resource "aws_sns_topic_subscription" "notify_email_sub" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.notify_email.arn
}

resource "aws_lambda_permission" "notify_email_sns_perm" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notify_email.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}
