# module.aws.aws_cloudwatch_event_rule.voice-gram-notification-trigger:
resource "aws_cloudwatch_event_rule" "voice-gram-notification-trigger" {
    name = "${var.PROJECT_NAME}-notification-trigger"
    schedule_expression = "rate(1 minute)"
    tags = local.tags
    is_enabled = false
}

# module.aws.aws_cloudwatch_event_target.voice-gram-notification-trigger-target:
resource "aws_cloudwatch_event_target" "voice-gram-notification-trigger-target" {
    arn = aws_lambda_function.voice-gram-notification.arn
    rule = aws_cloudwatch_event_rule.voice-gram-notification-trigger.name
}

# module.aws.aws_cloudwatch_log_group.voice-gram-notification-log:
resource "aws_cloudwatch_log_group" "voice-gram-notification-log" {
    name = "/aws/lambda/${aws_lambda_function.voice-gram-notification.function_name}"
    retention_in_days = 7
    tags = local.tags
}

# module.aws.aws_cloudwatch_log_group.voice-gram-skill-log:
resource "aws_cloudwatch_log_group" "voice-gram-skill-log" {
    name = "/aws/lambda/${aws_lambda_function.voice-gram-skill.function_name}"
    retention_in_days = 7
    tags = local.tags
}