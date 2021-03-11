# module.aws.aws_lambda_layer_version.voice-gram-layer:
resource "aws_lambda_layer_version" "voice-gram-layer" {
    compatible_runtimes = [
        "python3.8"
    ]
    description = ""
    layer_name = var.PROJECT_NAME
    source_code_hash = data.archive_file.zip-folders["layer"].output_base64sha256
    s3_bucket = aws_s3_bucket.voice-gram-bucket.bucket
    s3_key = aws_s3_bucket_object.voice-gram-artifacts["layer"].key
    s3_object_version = aws_s3_bucket_object.voice-gram-artifacts["layer"].version_id
}

# aws_lambda_function.voice-gram-skill:
resource "aws_lambda_function" "voice-gram-skill" {
    function_name = "${var.PROJECT_NAME}-skill"
    handler = "index.handler"
    publish = false
    layers = [
        "arn:aws:lambda:${var.REGION}:${data.aws_caller_identity.current.account_id}:layer:ffmpeg:2",
        aws_lambda_layer_version.voice-gram-layer.arn,
    ]
    memory_size = 192
    reserved_concurrent_executions = -1
    role = aws_iam_role.voice-gram-role.arn
    runtime = "python3.8"
    tags = local.tags
    timeout = 10

    source_code_hash = data.archive_file.zip-folders["skill"].output_base64sha256
    s3_bucket = aws_s3_bucket.voice-gram-bucket.bucket
    s3_key = aws_s3_bucket_object.voice-gram-artifacts["skill"].key
    s3_object_version = aws_s3_bucket_object.voice-gram-artifacts["skill"].version_id

    environment {
        variables = {
            "DEVICE" = "Echo"
            "VERSION" = "Voice Gram 1.0.0"
            "SYSTEM" = "Alexa"
            "TG_TOKEN" = var.TG_TOKEN
            "TG_ID" = var.TG_ID
            "TG_SECRET" = var.TG_SECRET
            "PROJECT_NAME" = var.PROJECT_NAME
            "SKILL_ID" = var.SKILL_ID
        }
    }

    timeouts {}

    tracing_config {
        mode = "PassThrough"
    }
}

# module.aws.aws_lambda_function.voice-gram-notification:
resource "aws_lambda_function" "voice-gram-notification" {
    function_name = "${var.PROJECT_NAME}-notification"
    handler = "index.handler"
    layers = [
        aws_lambda_layer_version.voice-gram-layer.arn,
    ]
    memory_size = 192
    role = aws_iam_role.voice-gram-role.arn
    runtime = "python3.8"
    tags = local.tags
    timeout = 60

    source_code_hash = data.archive_file.zip-folders["notification"].output_base64sha256
    s3_bucket = aws_s3_bucket.voice-gram-bucket.bucket
    s3_key = aws_s3_bucket_object.voice-gram-artifacts["notification"].key
    s3_object_version = aws_s3_bucket_object.voice-gram-artifacts["notification"].version_id

    environment {
        variables = {
            "DEVICE" = "Echo"
            "VERSION" = "Voice Gram 1.0.0"
            "SYSTEM" = "Alexa"
            "TG_TOKEN" = var.TG_TOKEN
            "TG_ID" = var.TG_ID
            "TG_SECRET" = var.TG_SECRET
            "ALEXA_ID" = var.ALEXA_ID
            "ALEXA_SECRET" = var.ALEXA_SECRET
            "ALEXA_USER_ID" = var.ALEXA_USER_ID
            "ENDPOINT" = var.ENDPOINT
            "LOCALE" = var.LOCALE
        }
    }

    timeouts {}

    tracing_config {
        mode = "PassThrough"
    }
}

resource "aws_lambda_permission" "alexa-invocation-permission" {
    statement_id = "AllowExecutionFromAlexa"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.voice-gram-skill.function_name
    principal = "alexa-appkit.amazon.com"
    event_source_token = var.SKILL_ID
}

resource "aws_lambda_permission" "cloudwatch-rule-invocation-permission" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.voice-gram-notification.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.voice-gram-notification-trigger.arn
}