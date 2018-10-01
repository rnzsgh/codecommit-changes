# AWS CodeCommit CloudWatch Events

Example Lambda function that showcases how to retrieve commits for a git push event.


See the [AWS CodeCommit Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#codecommit_event_type) documentation for additional information on the message payload.

### Setup

* Create a SNS topic
* Subscribe to the SNS topic
  * For email notification, create a subscription to the topic and click the confirmation in the email received
* Create a Lambda function
  * 5m timeout
  * Python 2.7
  * Handler function: lambda_function.handler
  * Environment variable: OUTPUT_TOPIC_ARN = SNS topic ARN created in previous step
  * Execution role needs the ability to write to CloudWatch Logs, publish to the SNS topic created and read from CodeCommit
* Create a CloudWatch Event Rule
  * Service Name: CodeCommit
  * Event Type: CodeCommit Repository State Change
  * Limit the event to a specific resource ARN or leave blank for all repos

The CloudWatch Event pattern should look like (if you specify the resource arn - "resources" will not be present if not):

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

The sample deploy.sh script showcases how to push updates to the Lambda function. You must create the function before deploying
