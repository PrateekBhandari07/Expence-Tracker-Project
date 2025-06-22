# 💰 Expense Tracker (Serverless Architecture)

A full-stack serverless expense tracking application that enables users to manage their daily expenses and visualize their spending patterns. Built using modern AWS services, this project includes a responsive frontend and a scalable, event-driven backend with automatic email alerts when spending crosses a defined threshold.

---

## 📝 Project Description

This Expense Tracker allows users to **add, update, delete, and view expenses**, while also displaying a **real-time bar chart** summary by category. The app leverages **AWS Lambda** as the backend, with **API Gateway** as the REST interface and **DynamoDB** for storage. When a user’s total expenses exceed **₹10,000**, an alert is triggered and sent via **AWS SNS (Simple Notification Service)** as an email notification.

The frontend is a single-page application built with **HTML, CSS, Bootstrap, and Chart.js**, hosted as a static site on **Amazon S3**.

---

## 🚀 Tech Stack

| Layer       | Technology                            |
|-------------|----------------------------------------|
| Frontend    | HTML, CSS, Bootstrap, Chart.js         |
| Backend     | AWS Lambda (Python), API Gateway       |
| Database    | Amazon DynamoDB                        |
| Notification| AWS SNS (email alert system)           |
| Hosting     | Amazon S3 (static website hosting)     |

---

## ⚙️ Project Setup

### 🔧 Frontend (Static Website on S3)

1. Place your `index.html` (and any other static assets) in a folder.
2. Go to AWS S3 → Create a new bucket (enable static website hosting).
3. Upload `index.html` to the bucket.
4. Enable **public access** to files.
5. Set index document: `index.html`
6. Access your frontend using the S3 website endpoint.

---

### 🔧 Backend (AWS Lambda + API Gateway + DynamoDB + SNS)

#### 1. **Create a DynamoDB Table**
- **Table Name**: `Expense`
- **Partition Key**: `userId` (String)
- **Sort Key**: `expenseId` (String)

#### 2. **Create SNS Topic**
- Create a topic (e.g., `ExpenseAlerts`)
- Subscribe your email (confirm it via mail)
- Copy the **Topic ARN**

#### 3. **Create the Lambda Function**
- Runtime: Python 3.9+
- Use the `lambda_function.py` (from `backend/`) as the source code.
- Set environment variables or hardcode `SNS_TOPIC_ARN` and `userId`.

#### 4. **Attach Permissions**
- Attach policies for:
  - `AmazonDynamoDBFullAccess`
  - `AmazonSNSFullAccess`
  - `AWSLambdaBasicExecutionRole`

#### 5. **Create API Gateway**
- Create a **REST API** (HTTP API also works).
- Define the following endpoints:
  - `POST /expenses` → Add expense
  - `GET /expenses` → Get all expenses
  - `PUT /expenses/{id}` → Update expense
  - `DELETE /expenses/{id}` → Delete expense
- Integrate each route with the Lambda.

#### 6. **Enable CORS**
Ensure all methods in API Gateway have:
```http
Access-Control-Allow-Origin: *

#### 📊 Output

-Adding a New Expense
![image](https://github.com/user-attachments/assets/79a1cc66-cc9e-4112-9d19-632d6e349a38)

-Expense Table View
![image](https://github.com/user-attachments/assets/b3e6e868-9bd4-498c-ab80-df6af215aefb)

-Expense Chart
![image](https://github.com/user-attachments/assets/7c55b7bf-5fb7-4200-ae88-19839048fda9)

-SNS Alert Example
-As you can see, my total expenses have crossed the threshold of ₹10,000.
-I received an SNS email notification as shown below:

![image](https://github.com/user-attachments/assets/013bda67-d08e-44ff-b97e-f4ac7a4841e1)




