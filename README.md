# Agentic AWS Demo 🤖

An AI-powered AWS infrastructure management system that allows you to manage cloud resources through natural language conversations. Built with Claude AI, FastAPI, and Streamlit.

## 🌟 Features

- **Natural Language Interface**: Manage AWS resources using plain English
- **AI-Powered Tool Selection**: Claude automatically chooses the right AWS operations
- **Real AWS Integration**: Actually creates and manages AWS resources
- **Intelligent Responses**: Get both technical data and human explanations
- **CloudWatch Monitoring**: Query logs and debug Lambda functions
- **Conversational AI**: Context-aware conversations with memory

## 🏗️ Architecture

```
User (Streamlit) → FastAPI → AI Agent (Claude) → AWS APIs → Response
```

### Components:
- **Frontend**: Streamlit chat interface
- **Backend**: FastAPI server with CORS
- **AI Agent**: Claude 3.5 Sonnet with function calling
- **AWS Integration**: Cloud Control API + CloudWatch Logs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with appropriate permissions
- Anthropic API key

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd agentic-aws-demo
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root:

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AWS Credentials (for demo purposes)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional: AWS Role ARN for better security
# AWS_ROLE_ARN=arn:aws:iam::ACCOUNT:role/ROLE_NAME
```

### 5. AWS Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudcontrol:CreateResource",
                "cloudcontrol:GetResource",
                "cloudcontrol:UpdateResource",
                "cloudcontrol:DeleteResource",
                "cloudcontrol:ListResources",
                "cloudcontrol:GetResourceRequestStatus"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBuckets",
                "logs:FilterLogEvents",
                "logs:DescribeLogGroups"
            ],
            "Resource": "*"
        }
    ]
}
```

### 6. Run the Application

#### Start the Backend (FastAPI):
```bash
uvicorn main:app --reload --port 8000
```

#### Start the Frontend (Streamlit):
```bash
streamlit run chat.py --server.port 8501
```

### 7. Access the Application

Open your browser and go to: `http://localhost:8501`

## 💬 Usage Examples

### Infrastructure Management

```
User: "Create an S3 bucket for my photos"
AI: I'll create an S3 bucket for your photos. What would you like to name it?

User: "my-photo-bucket-2024"
AI: [Creates bucket] ✅ Successfully created S3 bucket 'my-photo-bucket-2024'
```

### Monitoring & Debugging

```
User: "Check for errors in my lambda function 'user-authentication'"
AI: [Queries CloudWatch Logs] Found 3 errors in the last hour:
- Authentication failed for user 'john@example.com'
- Invalid token format detected
- Database connection timeout
```

### Resource Listing

```
User: "Show me all my S3 buckets"
AI: [Lists resources] You have 5 S3 buckets:
- my-photo-bucket-2024
- data-backup-bucket
- static-website-assets
- ...
```

## 🛠️ Available Tools

### 1. AWS Cloud Control API
- **Create resources**: S3 buckets, EC2 instances, Lambda functions
- **List resources**: View existing infrastructure
- **Read resources**: Get detailed resource information
- **Update/Delete**: Modify or remove resources

### 2. CloudWatch Logs
- **Query error logs**: Find issues in Lambda functions
- **Time-based filtering**: Search logs by time range
- **Error analysis**: Get detailed error information

## 🔧 Configuration

### Tool Definitions
Tools are defined in `tools.json`:
- `aws_cloud_control`: Infrastructure management operations
- `cloudwatch_logs`: Log querying and monitoring

### System Prompts
AI behavior is controlled by prompts in `prompt.py`:
- Parameter validation rules
- Error handling instructions
- Response formatting guidelines

## 🚨 Troubleshooting

### Common Issues

#### 1. Anthropic API Overloaded (Error 529)
```
Error: Overloaded
```
**Solution**: Restart the app. Context Window size might have exceeded (Need to be managed for production).

#### 2. AWS Connection Failed
```
Error: AWS connection failed
```
**Solutions**:
- Check your AWS credentials in `.env`
- Verify AWS permissions
- Ensure AWS region is correct

#### 3. Resource Not Created
```
Status: success, but no resource in AWS
```
**Cause**: Cloud Control API is asynchronous
**Solution**: Check resource status and the error details using the request token that was returned by the AWS API. 
```bash
aws cloudcontrol get-resource-request-status --request-token YOUR_TOKEN
```

### Debug Mode

Enable detailed logging by checking the console output:
- AWS API calls and responses
- AI tool selection process
- Error details and stack traces

## 🔒 Security Considerations

### Current Setup (Demo)
- Uses AWS access keys (not recommended for production)
- Basic authentication

### Production Recommendations
1. **Use IAM Roles** instead of access keys
2. **Implement AWS SSO** for user authentication
3. **Use least privilege** permissions
4. **Enable CloudTrail** for audit logging
5. **Implement proper error handling** and logging

### Role-Based Access Example
```python
# Instead of access keys, use role assumption
sts_client = boto3.client('sts')
assumed_role = sts_client.assume_role(
    RoleArn='arn:aws:iam::ACCOUNT:role/DemoRole',
    RoleSessionName='AgenticAIDemo'
)
```

## 📁 Project Structure

```
agentic-aws-demo/
├── aws_agent.py          # Main AI agent logic
├── aws_config.py         # AWS configuration
├── prompt.py             # AI system prompts
│── main.py               # FastAPI server
│── processor.py          # Request processor
│── app.py                # Streamlit interface
│── tools.json            # Tool definitions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md             # This file
```


## 🔮 Future Enhancements

- **Additional AWS services** (RDS, ECS, etc.)
- **Cost management** tools
- **Infrastructure templates**
- **Multi-account support**
- **Enhanced security** features
- **Real-time monitoring** dashboard

---
