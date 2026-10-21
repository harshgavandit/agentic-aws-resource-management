# Agentic AWS Resource Management

A chat app for working with AWS resources using plain English. You describe what you need, Claude selects the AWS operation, and the app runs it using your configured AWS credentials and explains the result.

The app can:

- Submit requests to create resources through AWS Cloud Control API.
- List existing resources and read their configuration.
- Search a Lambda function's CloudWatch logs for `ERROR` messages over a chosen time period.
- Keep conversation history during the current chat session.

For example, you can ask it to list your S3 buckets, read a bucket's configuration, create a bucket with a name you provide, or check a Lambda function's recent errors.

The chat interface uses Streamlit, the backend uses FastAPI, and AWS calls use boto3. Claude handles tool selection and summarizes the results.

Resource creation runs asynchronously; the app submits the request but does not wait for provisioning to finish. Update and delete operations are not implemented.
