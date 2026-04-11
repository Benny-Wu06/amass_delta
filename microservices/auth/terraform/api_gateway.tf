# creates api gateway
resource "aws_apigatewayv2_api" "auth_api" {
  name          = "auth-service-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
  }
}

# automatic deploy changes 
resource "aws_apigatewayv2_stage" "auth_stage" {
  api_id      = aws_apigatewayv2_api.auth_api.id
  name        = "$default"
  auto_deploy = true
}

# connects API gateway to your lambda
resource "aws_apigatewayv2_integration" "auth_integration" {
  api_id                 = aws_apigatewayv2_api.auth_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.auth_lambda.invoke_arn
  payload_format_version = "2.0"
}

# route for signup
resource "aws_apigatewayv2_route" "signup" {
  api_id    = aws_apigatewayv2_api.auth_api.id
  route_key = "POST /auth/signup"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# route for login
resource "aws_apigatewayv2_route" "login" {
  api_id    = aws_apigatewayv2_api.auth_api.id
  route_key = "POST /auth/login"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# route for logout
resource "aws_apigatewayv2_route" "logout" {
  api_id    = aws_apigatewayv2_api.auth_api.id
  route_key = "POST /auth/logout"
  target    = "integrations/${aws_apigatewayv2_integration.auth_integration.id}"
}

# rrints the URl after deployment
output "auth_api_url" {
  value = aws_apigatewayv2_stage.auth_stage.invoke_url
}