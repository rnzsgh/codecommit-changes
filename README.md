# AWS CodeCommit CloudWatch Events

Example Lambda function that showcases how to retrieve commits for a git push event.


See the [AWS CodeCommit Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/EventTypes.html#codecommit_event_type) documentation for additional information on the message payload.

Steps to setup:

* Create a SNS topic
* Subscribe to the SNS topic
* Create a Lambda function
  * 5m timeout
  * Python 2.7

