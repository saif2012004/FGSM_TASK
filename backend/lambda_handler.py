"""
AWS Lambda handler for FGSM FastAPI application
This file adapts the FastAPI app for serverless deployment on AWS Lambda
"""

from mangum import Mangum
from app_fgsm import app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")

# For AWS Lambda, we need to handle the event and context
def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: AWS Lambda event object
        context: AWS Lambda context object
        
    Returns:
        Response in the format expected by API Gateway
    """
    return handler(event, context)
