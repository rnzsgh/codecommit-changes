# AWS CodeCommit CloudWatch Events

Example Lambda function that showcases how to retrieve commits for a git push event.


See the [AWS CodeCommit Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#codecommit_event_type) documentation for additional information on the message payload.

Steps to setup:

* Create a SNS topic
  * For email notification, create a subscription to the topic and click the confirmation in the email sent
* Subscribe to the SNS topic
* Create a Lambda function
  * 5m timeout
  * Python 2.7
  * Handler function: lambda_function.handler
  * Environment variable: OUTPUT_TOPIC_ARN = SNS topic ARN created in previous step
  * Execution role needs the ability to write to CloudWatch Logs, publish to the SNS topic created and read from CodeCommit

The CloudWatch Event pattern should look like:

```
{
  "source": [
    "aws.codecommit"
  ],
  "detail-type": [
    "CodeCommit Repository State Change"
  ],
  "resources": [
    "arn:aws:codecommit:us-east-1:ACCOUNT_ID:REPO_OR_*_FOR_ALL"
  ]
}
```

