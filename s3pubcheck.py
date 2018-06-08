import boto3
import sys
from botocore.exceptions import ClientError
import json


# Replace SENDER & RECEPIENT with email addresses.
# If your account is still in the "sandbox", SES requires that the address be verified.

SENDER = ""
RECIPIENT = ""
# Replace AWS_REGION appropriately
AWS_REGION = ""

# Gets Account ID - You can place this Lambda across all your AWS accounts
account_id=boto3.client('sts').get_caller_identity().get('Account')
SUBJECT = "S3 Public Bucket Notification for Account:" + str(account_id)

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client2 = boto3.client('ses',region_name=AWS_REGION)


def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    count=0
    bucket_policy={}
    principle={}
    effect={}
    account_id=boto3.client('sts').get_caller_identity().get('Account')
    email_str="S3 Public Bucket Notification for Account:" + str(account_id) + "\n" + "*****************************************" + "\n"

    for bucket in s3.buckets.all():
        bucket_name=bucket.name
        createDate=bucket.creation_date
        bucket_acl=s3.BucketAcl(bucket_name).grants
        #Checks Bucket Policies for Principal:* and Effect:Allow
        try:
         bucket_policy=json.loads(s3.BucketPolicy(bucket_name).policy)
         for i in range(0,len(bucket_policy['Statement'])):
          principle = bucket_policy['Statement'][i]['Principal']
          effect = bucket_policy['Statement'][i]['Effect']
          if "*" in principle and "Allow" in effect:
           count = count + 1
           email_str = str(email_str) + str(bucket_name) + " " + str(createDate) + " Bucket Policy" + "\n"
           break
          #print principle,effect,bucket_name
        except ClientError as e: # Handles buckets without any policy
         pass
        #Checks Bucket ACL for "AllUsers"
        if "AllUsers" in str(bucket_acl) and str(bucket_name) not in email_str:
    	    count=count+1
    	    email_str = str(email_str) + str(bucket_name) + " " + str(createDate) + "\n"
    count_str=str(count)	    
    filename=account_id+".txt"
    
    # We want to preserve the number of Public S3 buckets for each invocation. I have used S3 in this case.
    obj = s3.Object('ENTER S3 BUCKET NAME THAT STORES THIS VALUE', filename)
    s3_count=obj.get()['Body'].read().decode('utf-8') 
    print "S3 count: ",s3_count,"\n","Current Count:",count
    # Checks to see if current Bucket Count is more than previous bucket count
    if int(count) == int(s3_count):
        print "Bucket counts equal"
        print email_str
    if int(count) > int(s3_count):
        print "New public s3 bucket detected, sending email"
        print email_str
        emailResult(email_str,SUBJECT)
    ## Writes new public bucket count to the S3 bucket/account-id.txt
    s3.Bucket('ENTER S3 BUCKET NAME THAT STORES THIS VALUE').put_object(Key=filename, Body=count_str)
    

def emailResult(email_result,SUBJECT):
    #Provide the contents of the email.
    response = client2.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': CHARSET,
                    'Data': str(email_result)
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': SUBJECT,
            },
        },
        Source=SENDER
    )
