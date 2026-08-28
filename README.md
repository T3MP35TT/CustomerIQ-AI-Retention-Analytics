# CustomerIQ — AI-Powered Customer Intelligence & Retention Analytics

CustomerIQ is an end-to-end customer intelligence and retention analytics platform that combines **SQL, Python, Machine Learning, RFM analysis, Power BI, FastAPI, and Generative AI** to identify customers at risk of churn, quantify financial exposure, prioritize retention actions, and answer business questions using natural language.

🔗 **Live AI Demo:** https://customeriq-ai.onrender.com/

---

## 📌 Project Overview

Customer churn is not just a customer-retention problem — it is a **revenue and profitability problem**.

CustomerIQ transforms customer transaction, product, and interaction data into actionable retention intelligence by answering four key business questions:

- **Who is likely to churn?**
- **Which customers should we prioritize?**
- **How much revenue and profit are at risk?**
- **What does the customer data tell us?**

The platform combines predictive analytics, customer segmentation, financial risk analysis, interactive Power BI dashboards, and a natural-language AI query interface.

Instead of requiring users to know SQL or database structure, CustomerIQ allows them to ask questions such as:

> "Which customer segments generate the most revenue?"

> "What is the churn probability of C00002?"

> "Which customers have the highest expected revenue at risk?"

> "Which location has the highest revenue?"

The AI dynamically translates these questions into SQL, validates the generated query, executes it against the CustomerIQ SQLite database, and converts the verified result into a business-friendly answer.

---

# 🎯 Business Objectives

CustomerIQ was designed to:

- Identify customers with a high probability of churn
- Segment customers using RFM analysis
- Quantify expected revenue at risk
- Quantify expected profit at risk
- Prioritize customers for retention campaigns
- Identify high-value customers exposed to churn risk
- Understand customer purchasing and engagement behavior
- Analyze acquisition channels and locations
- Provide executive-level insights through Power BI
- Enable natural-language access to customer intelligence
- Provide a safe and controlled AI-to-SQL workflow

---

# 📊 Key Results

CustomerIQ analyzed **967 customers** and produced the following predictive insights:

| Metric | Result |
|---|---:|
| Total Customers | 967 |
| Predicted Churners | 158 |
| Predicted Churn Rate | 16.34% |
| Expected Revenue at Risk | ₹17.02M |
| Expected Profit at Risk | ₹3.59M |

### Key Retention Insight

The **Hibernating** RFM segment represents the primary retention focus:

- **230 customers**
- **132 predicted churners**
- **57.39% predicted churn rate**

This makes the segment the clearest concentration of predicted churn risk and an important target for retention campaigns.

---

# 🧠 Predictive Analytics

CustomerIQ uses a machine-learning churn model to estimate the probability that each customer will churn.

The resulting customer-level scoring dataset contains business-oriented model outputs including:

- Churn probability
- Predicted churn
- Churn risk
- Customer value
- Expected revenue at risk
- Expected profit at risk
- Retention score
- Retention priority
- RFM segment

These outputs are synchronized into the CustomerIQ SQLite database and used by both the Power BI reporting layer and the AI query system.

---

# 👥 RFM Customer Segmentation

CustomerIQ uses **Recency, Frequency, and Monetary (RFM)** analysis to understand customer behavior and value.

The RFM framework considers:

### Recency
How recently a customer purchased.

### Frequency
How frequently a customer purchased.

### Monetary
How much revenue a customer generated.

The analytical segmentation includes customer groups such as:

- Champions
- Loyal Customers
- Potential Loyalists
- At Risk
- Lost Customers
- New / Promising
- Needs Attention

RFM segmentation provides behavioral context alongside the machine-learning churn predictions.

This makes it possible to distinguish between customers who are simply inactive and customers who represent significant financial risk.

---

# 💰 Financial Risk Analysis

CustomerIQ goes beyond predicting churn.

It estimates the financial impact associated with customer risk.

### Expected Revenue at Risk

Represents the expected revenue exposed to churn risk based on the customer scoring layer.

### Expected Profit at Risk

Represents the expected gross profit exposed to churn risk.

This allows the business to move from:

**"Which customers might leave?"**

to:

**"Which customers might leave, and how much could the business lose?"**

---

# 📈 Power BI Dashboard

The Power BI dashboard provides an executive-level view of customer health, churn risk, financial exposure, and retention opportunities.

## Page 1 — Executive Overview

Provides a high-level view of:

- Customer base
- Revenue
- Profit
- Revenue at risk
- Profit at risk
- Predicted churn
- Customer segments
- RFM segments
- Retention insights

---

## Page 2 — Predictive Customer Risk

Focuses on identifying and prioritizing customers who require retention attention.

Key analysis includes:

- Churn probability
- Predicted churn
- Churn risk
- Customer value
- Expected revenue at risk
- Expected profit at risk
- Retention priority
- RFM segment
- High-risk customer identification

---

## Page 3 — CustomerIQ AI

Provides a natural-language interface for querying the CustomerIQ database.

Users can ask questions about:

- Customers
- Revenue
- Profitability
- Orders
- Products
- Locations
- Acquisition channels
- Customer segments
- RFM segments
- Customer engagement
- Churn
- Churn probability
- Revenue at risk
- Profit at risk
- Retention priority
- Individual customers

---

# 🤖 AI-Powered Customer Intelligence

The AI layer is designed as a **controlled natural-language-to-SQL analytics system**.

It is not a simple chatbot and it does not rely on predefined questions.

Users can ask arbitrary business questions, and the system dynamically determines how the question should be answered using the CustomerIQ database.

### Example

User:

> Which customer segments generate the most revenue?

The system generates a SQL query similar to:

```sql
SELECT
    customers.customer_segment AS segment,
    SUM(transactions.revenue) AS total_revenue
FROM customers
JOIN transactions
```
The query is then validated against the SQLite database before execution.

The verified result is finally converted into a concise business answer.

🏗️ AI Architecture
                         User Question
                              │
                              ▼
                       FastAPI Application
                              │
                              ▼
                       CustomerIQ QA Layer
                              │
                              ▼
                       Query Planner
                              │
                              ▼
                     Semantic Layer
                              │
                              ▼
                       Ollama Cloud
                    gpt-oss:20b-cloud
                              │
                              ▼
                    Generated SQL Plan
                              │
                              ▼
                       SQL Validation
                              │
                              ▼
                       Query Executor
                              │
                              ▼
                    CustomerIQ SQLite DB
                              │
                              ▼
                       Verified Result
                              │
                              ▼
                       Answer Generator
                              │
                              ▼
                    Business-Friendly Answer

🧩 Semantic Layer

The semantic layer provides the AI with a controlled description of the CustomerIQ database.

It defines:

Available tables
Available columns
Logical relationships
Business metrics
Derived metrics
RFM definitions
Churn definitions
Natural-language synonyms
SQL generation rules
Read-only query restrictions

The semantic layer helps the model understand the difference between concepts such as:

Revenue vs. gross revenue
Customer segment vs. RFM segment
Customer value vs. transaction revenue
Predicted churn vs. historical churn
Revenue at risk vs. total revenue

This reduces the risk of the model inventing database fields or generating incorrect joins.

🔄 Dynamic Query Planning

CustomerIQ uses a dynamic query planner rather than a collection of hardcoded question templates.

The user can ask questions that were never explicitly programmed into the application.

The planner determines:

What the user is asking
Which tables are required
Which metrics are required
What level of aggregation is appropriate
Which filters are required
What SQL should be generated
What the expected result grain should be

The resulting structured plan contains:

SQL
Intent
Tables Used
Result Grain
🛡️ SQL Safety & Validation

Generated SQL is not executed blindly.

CustomerIQ applies multiple safeguards before a query reaches the database.

Read-only enforcement

Only:

SELECT
WITH ... SELECT

queries are permitted.

The system rejects operations such as:

INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
REPLACE
ATTACH
DETACH
PRAGMA
VACUUM
REINDEX
ANALYZE
BEGIN
COMMIT
ROLLBACK
SAVEPOINT
Database validation

The generated SQL is validated against the actual SQLite database using SQLite query planning before execution.

This catches issues such as:

Invalid table names
Invalid column names
Incorrect SQL syntax
Invalid joins
Other database-level query errors

Only validated SQL is passed to the execution layer.

🧮 Query Execution

After validation, the query executor runs the SQL against:

database/customeriq.db

The resulting data is treated as the source of truth.

The answer-generation layer is instructed to use only the verified result.

This prevents the language model from independently inventing or recalculating business numbers.

💬 Answer Generation

The verified query result is passed back to the AI answer-generation layer.

The model converts the structured result into a concise business response.

For example:

The customer segments that generate the most revenue are:

1. High — ₹252,162,934
2. Medium — ₹180,537,553
3. Low — ₹4,105,891

The answer layer is explicitly instructed to:

Use only verified results
Preserve numerical values
Preserve result ordering
Avoid inventing information
Include requested metrics
Format currency appropriately
Keep answers concise
Avoid exposing internal implementation details
☁️ Cloud Deployment

The AI application is deployed as a cloud service using Render.

The production architecture is:

                       Internet User
                            │
                            ▼
                    Render Web Service
                            │
                            ▼
                       FastAPI API
                            │
                            ▼
                     CustomerIQ AI
                            │
                            ▼
                      Ollama Cloud
                            │
                            ▼
                   gpt-oss:20b-cloud
                            │
                            ▼
                  CustomerIQ SQLite DB

The application is accessible through the live demo:

🔗 https://customeriq-ai.onrender.com/

🔐 Environment Configuration

Sensitive credentials are not stored in the GitHub repository.

The application uses environment variables for configuration.

Example:

OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_MODEL=gpt-oss:20b-cloud

The .env file is excluded from version control using .gitignore.

For production deployment, environment variables are configured directly in the Render service.

🗄️ Database

CustomerIQ uses a SQLite database:

database/
└── customeriq.db

The database contains five primary analytical tables:

customers
transactions
interactions
products
customer_scores
Logical relationships
customers.customer_id
        │
        ├──────── transactions.customer_id
        │
        ├──────── interactions.customer_id
        │
        └──────── customer_scores.customer_id

products.product_id
        │
        └──────── transactions.product_id
📋 Core Database Tables
customers

Customer profile and acquisition information.

Includes:

Customer ID
Signup date
Customer segment
Location
Acquisition channel
Age
Gender
transactions

Customer purchase history.

Includes:

Transaction ID
Customer ID
Product ID
Transaction date
Quantity
Price
Discount
Gross revenue
Net revenue
Transaction year/month
interactions

Customer engagement activity.

Includes:

Views
Clicks
Add-to-cart events
Email opens
Interaction channel
Interaction timestamp
products

Product catalogue and profitability information.

Includes:

Product ID
Category
Price
Cost
Launch date
Gross margin
Margin percentage
customer_scores

Customer-level model and retention outputs.

Includes:

Customer value
Churn probability
Predicted churn
Churn risk
Retention priority
Expected revenue at risk
Expected profit at risk
Retention score
RFM segment
🧪 Example AI Questions

CustomerIQ can answer questions such as:

Which customer segments generate the most revenue?

Which acquisition channel generates the most revenue?

Which location has the highest revenue?

Which customer segment has the most customers?

What is the average customer value?

What is the average customer value of high-risk customers?

How much revenue is at risk?

How many customers have churn probability above 80%?

What percentage of customers are predicted to churn?

Which RFM segment has the highest revenue at risk?

Which RFM segment has the highest churn rate?

Give me the top 10 high-risk customers.

Which customers have the highest expected revenue at risk?

Tell me about C00002.

What is the churn probability of C00002?

How much revenue is C00002 putting at risk?

The system is not limited to these examples.

They demonstrate the types of business questions the architecture can support.

🔄 Customer Score Synchronization

The machine-learning scoring output is synchronized into the CustomerIQ database using:

ai/sync_customer_scores.py

The synchronization process:

Loads the scored customer dataset
Connects to the CustomerIQ SQLite database
Updates the customer_scores table
Inserts customer-level model outputs
Makes the scoring results available to the AI and analytics layers

The current scoring dataset contains:

967 customers
📁 Project Structure
CustomerIQ/
│
├── ai/
│   ├── analytics_engine.py
│   ├── app.py
│   ├── customeriq_qa.py
│   ├── prompts.py
│   ├── query_executor.py
│   ├── query_planner.py
│   ├── semantic_layer.py
│   ├── sync_customer_scores.py
│   ├── verify_customer_value.py
│   └── requirements.txt
│
├── database/
│   └── customeriq.db
│
├── data/
│   └── churn_scored_customers.csv
│
├── sql/
│   └── 10_export_churn_dataset.sql
│
├── frontend/
│   └── ...
│
├── inspect_database.py
├── .env
├── .gitignore
└── README.md

.env is intentionally excluded from GitHub because it contains the Ollama API credential.

⚙️ Technology Stack
Technology	Purpose
Python	Data processing and application logic
SQLite	Analytical database
SQL	Data transformation and analytics
Pandas	Data processing
Machine Learning	Churn prediction
RFM Analysis	Customer segmentation
Power BI	Business intelligence and visualization
FastAPI	REST API and web application backend
Ollama Cloud	Generative AI / LLM inference
gpt-oss:20b-cloud	Natural-language query generation and answer generation
Render	Cloud deployment
Git / GitHub	Version control and project management
🔐 Design Principles

CustomerIQ was designed around several principles:

1. Business-first analytics

The system focuses on business questions rather than simply producing technical metrics.

2. Verified data

AI-generated answers are based on results calculated directly from the CustomerIQ database.

3. Controlled AI-to-SQL

The LLM receives an explicit semantic layer and SQL safety rules.

4. No hardcoded question templates

The system dynamically interprets natural-language questions.

5. Read-only analytics

The AI query layer is restricted to read-only SQL.

6. Separation of prediction and outcome

For churn modeling, historical customer behavior is used as model input while future transactions are treated as outcomes rather than predictive features.

7. Actionable retention intelligence

The objective is not simply to predict churn, but to identify where financial risk exists and which customers deserve attention first.

🚀 Running Locally
1. Clone the repository
git clone https://github.com/T3MP35TT/CustomerIQ.git
cd CustomerIQ
2. Install dependencies
cd ai
python -m pip install -r requirements.txt
3. Configure environment variables

Create a .env file in the project root:

OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_MODEL=gpt-oss:20b-cloud
4. Start the FastAPI application

From the ai directory:

python -m uvicorn app:app --reload

The application will be available at:

http://127.0.0.1:8000
🌐 API

CustomerIQ exposes a FastAPI endpoint for natural-language questions.

Health Check
GET /health

Example response:

{
  "status": "healthy",
  "service": "CustomerIQ AI API"
}
Ask CustomerIQ
POST /ask

Request:

{
  "question": "Which customer segments generate the most revenue?"
}

Response:

{
  "question": "Which customer segments generate the most revenue?",
  "answer": "The customer segments that generate the most revenue are..."
}
📌 Project Highlights

CustomerIQ demonstrates the integration of:

SQL analytics
Data engineering
Customer segmentation
Machine learning
Churn prediction
Financial risk modeling
Power BI
Natural-language analytics
LLM-powered SQL generation
Semantic data modeling
SQL validation
FastAPI
Cloud deployment
GitHub-based development workflow

The key objective was to move beyond a traditional dashboard and build a business-facing customer intelligence system where users can explore customer data through both visual analytics and natural language.

🎯 Final Outcome

CustomerIQ brings together predictive analytics and generative AI into a single customer-retention intelligence platform.

The workflow moves from:

Raw Customer Data
        ↓
Data Preparation
        ↓
Customer Analytics
        ↓
RFM Segmentation
        ↓
Churn Prediction
        ↓
Financial Risk Estimation
        ↓
Power BI Dashboard
        ↓
Natural-Language AI
        ↓
Business Decision

Instead of simply reporting that a customer is likely to churn, CustomerIQ helps answer the more important business question:

"Who should we act on first, and how much value is at risk?"

🔗 Links

Live AI Demo:
https://customeriq-ai.onrender.com/

GitHub Repository:
https://github.com/T3MP35TT/CustomerIQ
    ON customers.customer_id = transactions.customer_id
GROUP BY customers.customer_segment
ORDER BY total_revenue DESC;
