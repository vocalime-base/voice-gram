# module.aws.aws_s3_bucket.voice-gram-bucket:
resource "aws_s3_bucket" "voice-gram-bucket" {
    arn = "arn:aws:s3:::${var.PROJECT_NAME}"
    bucket = var.PROJECT_NAME
    hosted_zone_id = "Z1BKCTXD74EZPE"
    request_payer = "BucketOwner"
    tags = local.tags

    lifecycle_rule {
        abort_incomplete_multipart_upload_days = 1
        enabled = true
        id = "Delete audio files"
        prefix = "audio"
        tags = {}

        expiration {
            days = 1
            expired_object_delete_marker = false
        }

        noncurrent_version_expiration {
            days = 1
        }
    }

    lifecycle_rule {
        abort_incomplete_multipart_upload_days = 1
        enabled = true
        id = "Delete old artifact versions"
        prefix = "artifacts"
        tags = {}

        noncurrent_version_expiration {
            days = 30
        }
    }

    versioning {
        enabled = true
        mfa_delete = false
    }
}

# module.aws.aws_s3_bucket_policy.voice-gram-bucket-policy:
resource "aws_s3_bucket_policy" "voice-gram-bucket-policy" {
    bucket = aws_s3_bucket.voice-gram-bucket.bucket
    policy = jsonencode(
    {
        Statement = [
            {
                Action = "s3:GetObject"
                Effect = "Allow"
                Principal = "*"
                Resource = "arn:aws:s3:::${aws_s3_bucket.voice-gram-bucket.bucket}/icons/*"
                Sid = "AddPerm"
            },
        ]
        Version = "2012-10-17"
    }
    )
}

# module.aws.aws_s3_bucket_public_access_block.voice-gram-bucket-public-access:
resource "aws_s3_bucket_public_access_block" "voice-gram-bucket-public-access" {
    block_public_acls = true
    block_public_policy = false
    bucket = aws_s3_bucket.voice-gram-bucket.bucket
    ignore_public_acls = true
    restrict_public_buckets = false
}

data "archive_file" "zip-folders" {
    output_path = "../skill/lambda/builds/${each.key}.zip"
    type = "zip"
    for_each = toset(local.functions)
    source_dir = each.key == "layer" ? "../skill/lambda/.aws-sam/build/${each.key}" : "../skill/lambda/${each.key}"
}

resource "aws_s3_bucket_object" "voice-gram-artifacts" {
    for_each = toset(local.functions)
    bucket = aws_s3_bucket.voice-gram-bucket.bucket
    key = "artifacts/${each.key}"
    source = data.archive_file.zip-folders[each.key].output_path
    etag = data.archive_file.zip-folders[each.key].output_md5
}