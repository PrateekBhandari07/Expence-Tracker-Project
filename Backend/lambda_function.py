import json
import boto3
import uuid
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Prateek')

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:641017921669:Prateek'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    method = event['httpMethod']

    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'CORS preflight response'})
        }
    elif method == 'POST':
        return add_expense(event)
    elif method == 'GET':
        return get_expenses(event)
    else:
        return {
            'statusCode': 405,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

def add_expense(event):
    try:
        body = json.loads(event['body'])
        user_id = body['userId']
        expense_id = str(uuid.uuid4())

        item = {
            'userId': user_id,
            'expenseId': expense_id,
            'amount': Decimal(str(body['amount'])),
            'category': body['category'],
            'description': body.get('description', ''),
            'date': body['date']
        }

        table.put_item(Item=item)
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        expenses = response.get('Items', [])

        # Calculate total amount
        total_amount = sum(Decimal(str(exp['amount'])) for exp in expenses)

        # If total crosses 10000, send SNS alert
        if total_amount > 10000:
            message = (
                f"Total Expense Alert!\n\n"
                f"User ID: {user_id}\n"
                f"Total Expenses: ₹{total_amount}\n"
                f"Threshold: ₹10000\n\n"
                f"This is a cumulative alert for this you."
            )
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='🚨 Total Expense Limit Crossed!',
                Message=message
            )

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'message': 'Expense added successfully', 'expenseId': expense_id})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }

def get_expenses(event):
    try:
        user_id = event['queryStringParameters'].get('userId')

        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )

        expenses = response.get('Items', [])

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps(expenses, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
