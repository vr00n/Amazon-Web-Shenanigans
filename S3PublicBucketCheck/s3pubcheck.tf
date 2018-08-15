resource "aws_iam_role" "lambda_S3PublicBucketCheck_role" {
  name               = "lambda_S3PublicBucketCheck_role"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_S3PublicBucketCheck_AssumePolicy.json}"
}

data "aws_iam_policy_document" "lambda_S3PublicBucketCheck_AssumePolicy" {
  statement {
    sid     = ""
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_policy" "lambda_S3PublicBucketCheck_policy" {
  name   = "lambda_S3PublicBucketCheck_policy"
  policy = "${data.aws_iam_policy_document.lambda_S3PublicBucketCheck_policyDoc.json}"
}

data "aws_iam_policy_document" "lambda_S3PublicBucketCheck_policyDoc" {
  statement {
    sid    = ""
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    sid    = ""
    effect = "Allow"

    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
    ]

    resources = ["*"]
  }

  statement {
    sid    = ""
    effect = "Allow"

    actions = [
      "s3:Get*",
      "s3:List*",
    ]

    resources = ["*"]
  }

  statement {
    sid    = ""
    effect = "Allow"

    actions = [
      "s3:Put*",
      "s3:List*",
    ]

    resources = [
      "arn:aws:s3:::BUCKET/*",
      "arn:aws:s3:::BUCKET",
    ]
  }
}

resource "aws_iam_role_policy_attachment" "attach-to-role" {
  role       = "${aws_iam_role.lambda_S3PublicBucketCheck_role.name}"
  policy_arn = "${aws_iam_policy.lambda_S3PublicBucketCheck_policy.arn}"
}

resource "aws_lambda_function" "S3PublicBucketCheck" {
  function_name    = "S3PublicBucketCheck"
  handler          = "S3PublicBucketCheck.lambda_handler"
  runtime          = "python2.7"
  filename         = "./S3PublicBucketCheck/S3PublicBucketCheck.py.zip"
  source_code_hash = "${base64sha256(file("./S3PublicBucketCheck/S3PublicBucketCheck.py.zip"))}"
  role             = "${aws_iam_role.lambda_S3PublicBucketCheck_role.arn}"
  timeout          = 300
}

resource "aws_cloudwatch_event_rule" "every_sixty_minutes" {
  name                = "every_sixty_minutes"
  description         = "Fires every thirty minutes"
  schedule_expression = "rate(60 minutes)"
}

resource "aws_cloudwatch_event_target" "S3PublicBucketCheck_lambda" {
  rule      = "${aws_cloudwatch_event_rule.every_sixty_minutes.name}"
  target_id = "S3PublicBucketCheck_lambda"
  arn       = "${aws_lambda_function.S3PublicBucketCheck.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_S3PublicBucketCheck_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.S3PublicBucketCheck.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.every_sixty_minutes.arn}"
}
