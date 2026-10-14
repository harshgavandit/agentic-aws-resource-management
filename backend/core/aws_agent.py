import anthropic
import json
import os
from dotenv import load_dotenv
from backend.config.aws_config import AWSConfig
from typing import Dict, Any, List
from backend.config.prompt import SYSTEM_PROMPT, SUMMARY_PROMPT
from datetime import datetime, timedelta

load_dotenv()

class AWSAgenticAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        self.aws_config = AWSConfig()
        
        # Test only AWS connection, skip Anthropic test to reduce API load
        self._test_aws_connection()
    
    def _test_aws_connection(self):
        """Test only AWS connection to reduce API load"""
        print("🔍 Testing AWS connection...")
        
        # Test AWS connection
        if not self.aws_config.validate_connection():
            raise Exception("AWS connection failed")
            
        print("AWS connection successful!")
        print("ℹAnthropic connection will be tested on first use")

    def _build_system_prompt(self) -> str:
        """Build system prompt for AWS operations"""
        return SYSTEM_PROMPT

    def _format_tools(self) -> List[Dict]:
        """Define tools for Claude"""
        json_path = os.path.join(os.path.dirname(__file__), "..", "tools", "tools.json")
        with open(json_path, "r") as f:
            tools = json.load(f)
        return tools 

    def _execute_aws_operation(self, operation: str, resource_type: str, 
                              identifier: str = None, properties: Dict = None, 
                              region: str = "us-east-1") -> Dict[str, Any]:
        """Execute AWS Cloud Control API operation"""
        
        try:
            session = self.aws_config.get_session()
            cloudcontrol = session.client('cloudcontrol', region_name=region)
            
            print(f"Executing {operation} on {resource_type}")
            print(f"Properties: {properties}")
            print(f"Region: {region}")
            
            if operation == "create":
                try:
                    response = cloudcontrol.create_resource(
                        TypeName=resource_type,
                        DesiredState=json.dumps(properties) if properties else "{}"
                    )
                    print(f"AWS Response: {response}")
                    
                    # Check if we actually got a valid response
                    if 'ProgressEvent' not in response:
                        return {
                            "status": "error",
                            "operation": operation,
                            "resource_type": resource_type,
                            "error": "Invalid response from AWS Cloud Control API",
                            "aws_response": str(response)
                        }
                    
                    request_token = response.get('ProgressEvent', {}).get('RequestToken')
                    if not request_token:
                        return {
                            "status": "error",
                            "operation": operation,
                            "resource_type": resource_type,
                            "error": "No request token received from AWS",
                            "aws_response": str(response)
                        }
                    
                    return {
                        "status": "success",
                        "operation": operation,
                        "resource_type": resource_type,
                        "request_token": request_token,
                        "message": f"Creating {resource_type}...",
                        "aws_response": str(response)
                    }
                    
                except Exception as create_error:
                    print(f"Create Resource Error: {create_error}")
                    return {
                        "status": "error",
                        "operation": operation,
                        "resource_type": resource_type,
                        "error": f"Failed to create resource: {str(create_error)}",
                        "aws_error": str(create_error)
                    }
                
            elif operation == "list":
                try:
                    response = cloudcontrol.list_resources(TypeName=resource_type)
                    print(f"List Response: {response}")
                    
                    resources = response.get('ResourceDescriptions', [])
                    return {
                        "status": "success",
                        "operation": operation,
                        "resource_type": resource_type,
                        "count": len(resources),
                        "resources": [json.loads(r.get('Properties', '{}')) for r in resources[:5]],  # Limit to 5
                        "aws_response": str(response)
                    }
                    
                except Exception as list_error:
                    print(f"List Resources Error: {list_error}")
                    return {
                        "status": "error",
                        "operation": operation,
                        "resource_type": resource_type,
                        "error": f"Failed to list resources: {str(list_error)}",
                        "aws_error": str(list_error)
                    }
                
            elif operation == "read" and identifier:
                try:
                    response = cloudcontrol.get_resource(
                        TypeName=resource_type,
                        Identifier=identifier
                    )
                    print(f"Read Response: {response}")
                    
                    return {
                        "status": "success",
                        "operation": operation,
                        "resource_type": resource_type,
                        "identifier": identifier,
                        "properties": json.loads(response['ResourceDescription']['Properties']),
                        "aws_response": str(response)
                    }
                    
                except Exception as read_error:
                    print(f"Read Resource Error: {read_error}")
                    return {
                        "status": "error",
                        "operation": operation,
                        "resource_type": resource_type,
                        "identifier": identifier,
                        "error": f"Failed to read resource: {str(read_error)}",
                        "aws_error": str(read_error)
                    }
                
            else:
                return {
                    "status": "error",
                    "message": f"Operation {operation} not fully implemented in demo"
                }
                
        except Exception as e:
            print(f"General AWS Operation Error: {e}")
            return {
                "status": "error",
                "operation": operation,
                "resource_type": resource_type,
                "error": f"General AWS operation failed: {str(e)}",
                "aws_error": str(e)
            }

    def _query_cloudwatch_logs(self, function_name: str, hours_back: int = 1) -> Dict[str, Any]:
        """Query CloudWatch Logs for Lambda function errors"""
        
        try:
            session = self.aws_config.get_session()
            logs_client = session.client('logs')
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            # Find log group for the Lambda function
            log_group_name = f"/aws/lambda/{function_name}"
            
            # Filter for ERROR level logs
            response = logs_client.filter_log_events(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000),
                filterPattern="ERROR"
            )
            
            error_logs = []
            for event in response.get('events', []):
                error_logs.append({
                    "timestamp": datetime.fromtimestamp(event['timestamp'] / 1000).isoformat(),
                    "message": event['message'],
                    "logStreamName": event['logStreamName']
                })
            
            return {
                "status": "success",
                "function_name": function_name,
                "hours_back": hours_back,
                "error_count": len(error_logs),
                "error_logs": error_logs[:10]  # Limit to 10 most recent errors
            }
            
        except Exception as e:
            return {
                "status": "error",
                "function_name": function_name,
                "error": str(e)
            }

    def _generate_summary(self, tool_name: str, tool_result: Dict[str, Any], user_question: str) -> str:
        """Generate natural language summary from tool results"""
        
        try:
            summary_prompt = SUMMARY_PROMPT.format(
            tool_name=tool_name,
            tool_result=json.dumps(tool_result, indent=2),
            user_question=user_question
        )
            
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=500,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"

    def process_request(self, user_input: str, history: List[Dict]) -> str:
        # Add user's message to incoming history
        history.append({"role": "user", "content": user_input})

        try:
            # Claude API call with tools
            response = self.client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=2000,
                system=self._build_system_prompt(),
                messages=history,
                tools=self._format_tools()
            )

            response_content = ""

            # Handle both text and tool_use responses
            for content_block in response.content:
                if content_block.type == "text":
                    print("Received a TEXT Response from LLM: ****************")
                    print("RAW Response from LLM:", content_block.text)
                    response_content += content_block.text

                elif content_block.type == "tool_use":
                    print("Received a Tool Use Request from LLM: ****************")
                    print("Tool Name:", content_block.name)
                    print("Tool Input:", content_block.input)
                    tool_name = content_block.name
                    tool_input = content_block.input

                    if tool_name == "aws_cloud_control":
                        result = self._execute_aws_operation(**tool_input)
                        #response_content += f"\n\n🔧 AWS Operation Result:\n{json.dumps(result, indent=2)}"
                        
                        # Generate natural language summary
                        summary = self._generate_summary(tool_name, result, user_input)
                        response_content += f"\n\n🤖 AI Summary:\n{summary}"
                    
                    elif tool_name == "cloudwatch_logs":
                        result = self._query_cloudwatch_logs(**tool_input)
                        response_content += f"\n\n📊 CloudWatch Logs Result:\n{json.dumps(result, indent=2)}"
                        
                        # Generate natural language summary
                        summary = self._generate_summary(tool_name, result, user_input)
                        response_content += f"\n\n🤖 AI Summary:\n{summary}"

            # Add assistant reply to history
            history.append({"role": "assistant", "content": response_content})

            return response_content

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(error_msg)
            return error_msg
