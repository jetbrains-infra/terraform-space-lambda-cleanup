data "aws_s3_bucket" "this" {
  bucket = var.s3_bucket
}

data "archive_file" "this" {
  source_file      = "${path.module}/lambda/lambda_function/main.py"
  output_path      = "${var.name}-backup-bucket-cleanup.zip"
  output_file_mode = "0666"
  type             = "zip"
}

resource "aws_lambda_function" "this" {
  function_name    = "${var.name}-backup-bucket-cleanup"
  handler          = "main.lambda_handler"
  role             = aws_iam_role.this.arn
  filename         = data.archive_file.this.output_path
  source_code_hash = data.archive_file.this.output_base64sha256
  runtime          = "python3.9"
  timeout          = 900

  environment {
    variables = {
      S3_BUCKET = data.aws_s3_bucket.this.id
    }
  }
}

resource "aws_lambda_permission" "this" {
  statement_id  = "${var.name}-backup-bucket-cleanup_allow"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.this.arn
}

resource "aws_cloudwatch_event_rule" "this" {
  name                = "${var.name}-backup-bucket-cleanup"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "this" {
  target_id = "${var.name}-backup-bucket-cleanup"
  arn       = aws_lambda_function.this.arn
  rule      = aws_cloudwatch_event_rule.this.name
}

resource "aws_iam_role" "this" {
  name = "${var.name}-backup-bucket-cleanup-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_execution_role" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


resource "aws_iam_role_policy" "this" {
  name = "${var.name}-backup-bucket-cleanup-policy"
  role = aws_iam_role.this.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListObjectVersions",
        "s3:ListBucketVersions",
        "s3:DeleteObjectVersion"
      ],
      "Resource": [
        "${data.aws_s3_bucket.this.arn}",
        "${data.aws_s3_bucket.this.arn}/*"
      ]
    }
  ]
}
EOF
}
