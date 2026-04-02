resource "aws_iam_role" "cisa_role" {
  name = "cisa_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "CisaLambda"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "s3_access" {
  name = "s3_write_permission"
  role = aws_iam_role.cisa_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${var.raw_bucket_arn}/*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cisa_basic_execution" {
  role       = aws_iam_role.cisa_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "cisa_insights" {
  role       = aws_iam_role.cisa_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}

resource "aws_iam_role" "enrich_role" {
  name = "enrich_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "enrichLambda"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "s3_enrich_access" {
  name = "s3_enrich_access"
  role = aws_iam_role.enrich_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject", "s3:GetObject"
        ]
        Resource = "${var.raw_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = ["${var.raw_bucket_arn}"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "enrich_basic_execution" {
  role       = aws_iam_role.enrich_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "enrich_insights" {
  role       = aws_iam_role.enrich_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLambdaInsightsExecutionRolePolicy"
}
