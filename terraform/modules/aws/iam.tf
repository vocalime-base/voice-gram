resource "aws_iam_role_policy_attachment" "voice-gram-role-amazon-s3-full-access" {
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    role = aws_iam_role.voice-gram-role.name
}

resource "aws_iam_role_policy_attachment" "voice-gram-role-lambda-basic-execution-role" {
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    role = aws_iam_role.voice-gram-role.name
}

data "aws_iam_policy_document" "voice-gram-role-trusted-entities" {
    statement {
        actions = ["sts:AssumeRole"]

        principals {
            type = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
    }
}

# module.iam.aws_iam_role.voice-gram-role:
resource "aws_iam_role" "voice-gram-role" {
    assume_role_policy = data.aws_iam_policy_document.voice-gram-role-trusted-entities.json
    description = "Allows Lambda functions to call AWS services on your behalf."
    force_detach_policies = false
    max_session_duration = 3600
    name = var.PROJECT_NAME
    path = "/"
    tags = local.tags
}