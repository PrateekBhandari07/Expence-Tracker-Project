import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Expense')

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:641017921669:hell'  

def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    path_params = event.get("pathParameters") or {}
    expense_id = path_params.get("id") if path_params else None

    user_id = "default_user"  # Hardcoded for now

    try:
        if method == "POST":
            if event.get("body") is None:
                raise ValueError("Missing request body")

            body = json.loads(event["body"])
            amount = Decimal(str(body["amount"]))
            category = body["category"]
            date = body["date"]
            description = body.get("description", "")

            expense_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()

            item = {
                'userId': user_id,
                'expenseId': expense_id,
                'amount': amount,
                'category': category,
                'description': description,
                'date': date,
                'createdAt': timestamp
            }

            table.put_item(Item=item)

            # Recalculate total expenses
            response = table.query(KeyConditionExpression=Key('userId').eq(user_id))
            total = sum(Decimal(str(entry['amount'])) for entry in response.get("Items", []))

            # Send alert if threshold crossed
            if total > Decimal("10000"):
                message = f"⚠️ Expense Limit Exceeded!\n\nUser: {user_id}\nTotal: ₹{float(total):,.2f}"
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="Expense Tracker Alert",
                    Message=message
                )

            return response_json(200, {
                "message": "Expense added successfully.",
                "id": expense_id,
                "total": float(total)
            })

        elif method == "GET":
            response = table.query(KeyConditionExpression=Key('userId').eq(user_id))
            items = sorted(response["Items"], key=lambda x: x.get("createdAt", ""), reverse=True)
            return response_json(200, items)

        elif method == "PUT" and expense_id:
            if event.get("body") is None:
                raise ValueError("Missing request body for update")

            body = json.loads(event["body"])
            update_expr = "SET "
            expr_attr_values = {}
            expr_attr_names = {}

            if "amount" in body:
                update_expr += "#a = :amount, "
                expr_attr_values[":amount"] = Decimal(str(body["amount"]))
                expr_attr_names["#a"] = "amount"
            if "description" in body:
                update_expr += "#d = :desc, "
                expr_attr_values[":desc"] = body["description"]
                expr_attr_names["#d"] = "description"

            update_expr = update_expr.rstrip(", ")

            table.update_item(
                Key={"userId": user_id, "expenseId": expense_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )

            return response_json(200, {"message": "Expense updated successfully."})

        elif method == "DELETE" and expense_id:
            table.delete_item(
                Key={"userId": user_id, "expenseId": expense_id}
            )
            return response_json(200, {"message": "Expense deleted successfully."})

        else:
            return response_json(405, {"error": f"{method} method not allowed or missing ID"})

    except Exception as e:
        return response_json(500, {"error": str(e)})

def response_json(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=str)
    }

