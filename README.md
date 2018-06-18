# S3-Public-Bucket-Check

An AWS lambda function that checks your account for Public S3 buckets and emails you whenever a new public bucket is created.

The function is triggered by a Cloudwatch event that fires every 60 minutes. 

Solves for [S3 Shaming](https://www.theregister.co.uk/2018/04/19/48_million_personal_profiles_left_exposed_by_data_firm_localblox/)
