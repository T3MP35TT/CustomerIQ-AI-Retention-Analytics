# CustomerIQ — AI-Powered Customer Intelligence & Retention Analytics

CustomerIQ is an end-to-end customer intelligence and retention analytics solution that combines **SQL, Python, Machine Learning, Power BI, FastAPI, SQLite, and Generative AI** to identify customers at risk of churn, quantify financial exposure, prioritize retention actions, and answer customer intelligence questions using natural language.

🔗 **Live AI Demo:** https://customeriq-ai.onrender.com/  
🔗 **GitHub Repository:** https://github.com/T3MP35TT/CustomerIQ


![CustomerIQ AI Assistant](./Snapshots/CustomerIQ%20AI%20Assistant%20Snapshot.png)

---

## 📌 Project Overview

Customer churn is not just a customer-retention problem — it is a revenue and profitability problem.

CustomerIQ transforms customer transaction and interaction data into actionable retention intelligence by answering four key business questions:

- **Who is likely to churn?**
- **Which customers should we prioritize?**
- **How much revenue and profit are at risk?**
- **What can the business learn from customer behavior?**

The project combines predictive analytics, customer segmentation, financial risk analysis, executive dashboards, and an AI-powered natural-language query interface.

---

## 🎯 Business Objectives

The project was designed to:

- Identify customers with a high probability of churn
- Segment customers using RFM analysis
- Quantify expected revenue and profit at risk
- Prioritize customers for retention campaigns
- Analyze customer purchasing and engagement behavior
- Evaluate acquisition channels and customer segments
- Provide executive-level insights through Power BI
- Allow users to ask business questions using natural language
- Dynamically translate business questions into SQL queries
- Return verified answers directly from the CustomerIQ database

---

## 📊 Key Results

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

This represents a significant concentration of predicted churn risk and provides a clear target for retention efforts.

---

## 🧠 Predictive Analytics

A machine-learning churn model was used to estimate each customer's probability of churn.

The scoring layer produces customer-level outputs including:

- Churn probability
- Predicted churn
- Churn risk
- Customer value
- Expected revenue at risk
- Expected profit at risk
- Retention score
- Retention priority
- RFM segment

These model outputs are synchronized into the CustomerIQ SQLite database and used by both the Power BI dashboard and AI query engine.

---

## 👥 RFM Customer Segmentation

Customers were segmented using **Recency, Frequency, and Monetary (RFM)** analysis.

The RFM analysis provides behavioral context around customer value and churn risk and supports customer-level retention prioritization.

RFM segments used in the CustomerIQ analytics layer include:

- Champions
- Loyal Customers
- Potential Loyalists
- At Risk
- Lost Customers
- New / Promising
- Needs Attention

---

## 🗄️ CustomerIQ Data Model

CustomerIQ uses a SQLite database containing five core analytical tables:

```text
customers
    │
    ├──────────────► transactions ─────────────► products
    │
    ├──────────────► interactions
    │
    └──────────────► customer_scores
```

### Core relationships

```text
customers.customer_id = transactions.customer_id

customers.customer_id = interactions.customer_id

transactions.product_id = products.product_id

customers.customer_id = customer_scores.customer_id
```

### Core tables

| Table | Purpose |
|---|---|
| `customers` | Customer profile, demographics, location, acquisition channel |
| `transactions` | Purchase, revenue, quantity, discount and transaction information |
| `interactions` | Customer digital engagement and interaction history |
| `products` | Product category, pricing and cost information |
| `customer_scores` | Churn predictions, customer value, retention scores and financial risk |

---

## 💰 Business Metrics

CustomerIQ uses documented analytical definitions so that business questions are translated consistently.

### Revenue

```text
SUM(transactions.revenue)
```

Net revenue after transaction discounts.

### Gross Revenue

```text
SUM(transactions.gross_revenue)
```

Revenue before transaction discounts.

### Orders

```text
COUNT(DISTINCT transactions.transaction_id)
```

### Customers

```text
COUNT(DISTINCT customer_id)
```

### Gross Profit

```text
SUM(transactions.revenue)
-
SUM(transactions.quantity * products.cost)
```

### Gross Margin %

```text
Gross Profit / Net Revenue × 100
```

### Average Order Value

```text
SUM(transactions.revenue)
/
COUNT(DISTINCT transactions.transaction_id)
```

### Customer Value

Customer value is taken from:

```text
customer_scores.customer_value
```

This prevents the AI layer from incorrectly assuming that a physical `customer_value` column exists in the transaction data.

---

## 🤖 AI-Powered Customer Intelligence

CustomerIQ includes a dynamic natural-language analytics engine.

Instead of relying on a fixed list of predefined questions, users can ask business questions such as:

```text
Which customer segments generate the most revenue?

Which acquisition channel generates the most revenue?

Which customers have the highest expected revenue at risk?

What is the average customer value?

Which location has the highest revenue?

How many customers have churn probability above 80%?

What is the churn probability of C00002?

Which RFM segment has the highest revenue at risk?
```

The system interprets the question, determines the required tables and metrics, generates SQL, validates the SQL against the database, executes the query, and converts the verified result into a natural-language answer.

---

## 🔄 Dynamic Natural Language → SQL Architecture

```text
                  User Business Question
                           │
                           ▼
                 Semantic Layer
                           │
                           ▼
                 Query Planner
                           │
                           ▼
              Natural Language → SQL
                           │
                           ▼
                   SQL Validation
                           │
                           ▼
                SQLite Query Execution
                           │
                           ▼
                 Verified Analytics
                           │
                           ▼
                  Ollama Cloud LLM
                           │
                           ▼
              Natural Language Answer
```

The analytical result is calculated from the CustomerIQ database first. The verified result is then passed to the language model to produce a readable response.

---

## 🧩 Semantic Layer

The `semantic_layer.py` module provides the AI with a controlled description of the CustomerIQ database.

It defines:

- Tables
- Columns
- Logical relationships
- Business metrics
- Derived concepts
- RFM definitions
- Churn definitions
- Natural-language synonyms
- SQL generation rules

This allows the AI to understand business terminology such as:

```text
revenue
sales
net sales
orders
customers
profit
customer value
revenue at risk
profit at risk
churn probability
high risk
RFM
engagement
```

The semantic layer also prevents the planner from relying on undocumented columns or incorrect relationships.

---

## 🧠 Dynamic SQL Query Planner

The `query_planner.py` module converts arbitrary business questions into structured SQL plans.

The planner returns:

```text
SQL
Intent
Tables Used
Result Grain
```

Example:

```sql
SELECT
    customers.customer_segment AS segment,
    SUM(transactions.revenue) AS total_revenue
FROM customers
JOIN transactions
    ON customers.customer_id = transactions.customer_id
GROUP BY customers.customer_segment
ORDER BY total_revenue DESC;
```

The system is therefore not restricted to predefined question templates.

---

## 🔐 SQL Safety & Validation

CustomerIQ applies multiple safeguards before executing generated SQL.

The AI is instructed to generate:

- SQLite-compatible SQL
- Exactly one SQL statement
- Read-only queries
- `SELECT` or `WITH ... SELECT` statements only
- Explicit joins
- Documented tables and columns only

The system rejects dangerous operations such as:

```text
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
COMMIT
ROLLBACK
```

Generated SQL is also validated against SQLite using query planning before execution.

---

## ⚙️ Query Execution

The query execution layer runs the validated SQL against the CustomerIQ SQLite database.

The execution flow is:

```text
Natural-language question
        ↓
Query planner
        ↓
Generated SQL
        ↓
Read-only validation
        ↓
SQLite validation
        ↓
Query execution
        ↓
Verified result
        ↓
AI response
```

This separation keeps the database calculation independent from the language-generation layer.

---

## ☁️ Ollama Cloud

The AI layer uses **Ollama Cloud** with:

```text
Model: gpt-oss:20b-cloud
```

The model is used for:

1. Natural-language → SQL planning
2. Verified analytics result → natural-language explanation

The model does not replace the analytical database. SQLite remains the source of truth for calculated results.

---

## 🚀 FastAPI Application

CustomerIQ exposes the AI functionality through a FastAPI application.

### API endpoints

#### Health Check

```text
GET /health
```

Used to verify that the API is running.

#### Ask CustomerIQ

```text
POST /ask
```

Example request:

```json
{
  "question": "Which customer segments generate the most revenue?"
}
```

Example response:

```json
{
  "question": "Which customer segments generate the most revenue?",
  "answer": "The customer segments that generate the most revenue are..."
}
```

---

## 🌐 Deployment

The CustomerIQ AI application is deployed as a cloud-hosted FastAPI service on **Render**.

The deployed application connects to the CustomerIQ database and Ollama Cloud, allowing users to interact with the AI analytics engine through the live application.

🔗 **Live Application:** https://customeriq-ai.onrender.com/

---

## 📈 Power BI Dashboard

The Power BI dashboard is structured around customer retention, financial exposure, and predictive risk.

![CustomerIQ Dashboard](./Snapshots/CustomerIQ%20Dashboard%20Snapshot.png)

### Page 1 — Executive Overview

Provides a high-level view of:

- Customer base
- Revenue exposure
- Profit exposure
- Churn risk
- Customer segments
- Retention insights

### Page 2 — Predictive Customer Risk

Focuses on:

- Predicted churn
- Customer risk
- Expected revenue at risk
- Customer value
- Retention priority
- High-risk customer identification
- Recommended retention actions

### Page 3 — CustomerIQ AI

Provides an entry point for natural-language customer intelligence questions.

Users can ask questions about:

- Customer churn
- Customer risk
- Revenue
- Profit
- Customer value
- Retention priorities
- Individual customers
- RFM segments
- Acquisition channels
- Locations
- Product performance

---

## 📁 Project Structure

```text
CustomerIQ/
│
├── ai/
│   ├── app.py
│   ├── customeriq_qa.py
│   ├── prompts.py
│   ├── semantic_layer.py
│   ├── query_planner.py
│   ├── query_executor.py
│   ├── analytics_engine.py
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
│   └── SQL analysis scripts
│
├── frontend/
│   └── CustomerIQ AI interface
│
├── inspect_database.py
│
├── .env.example
│
└── README.md
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing, analytics and AI application |
| SQLite | CustomerIQ analytical database |
| SQL | Data analysis and query execution |
| Pandas | Data preparation and analysis |
| Machine Learning | Churn prediction |
| RFM Analysis | Customer segmentation |
| Power BI | Executive dashboards and data storytelling |
| FastAPI | AI application API |
| Ollama Cloud | Generative AI |
| gpt-oss:20b-cloud | Natural-language reasoning and response generation |
| Render | Cloud deployment |
| Git / GitHub | Version control and deployment |

---

## 🔒 Environment Variables

The application uses environment variables for configuration and secrets.

Example:

```env
OLLAMA_API_KEY=your_ollama_cloud_api_key
OLLAMA_MODEL=gpt-oss:20b-cloud
CUSTOMER_DB_PATH=../database/customeriq.db
```

The actual `.env` file is not committed to GitHub.

---

## ▶️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/T3MP35TT/CustomerIQ.git
cd CustomerIQ
```

### 2. Install dependencies

```bash
cd ai
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file and add the required Ollama Cloud configuration.

```env
OLLAMA_API_KEY=your_ollama_cloud_api_key
OLLAMA_MODEL=gpt-oss:20b-cloud
```

### 4. Run the FastAPI application

From the `ai` directory:

```bash
python -m uvicorn app:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## 🧪 Example AI Questions

CustomerIQ can handle open-ended business questions rather than only predefined templates.

Examples:

```text
Which customer segments generate the most revenue?

Which acquisition channel generates the most revenue?

Which location has the highest revenue?

What is the average customer value?

What is the average customer value of high-risk customers?

How much revenue is at risk?

How many customers have churn probability above 80%?

Which customers have the highest expected revenue at risk?

Which RFM segment has the highest revenue at risk?

What is the churn probability of C00002?

How much revenue is C00002 putting at risk?

Show high-risk customers with customer value above 50000.
```

---

## 🔎 Example End-to-End Query

### User Question

```text
Which customer segments generate the most revenue?
```

### Generated SQL

```sql
SELECT
    customers.customer_segment AS segment,
    SUM(transactions.revenue) AS total_revenue
FROM customers
JOIN transactions
    ON customers.customer_id = transactions.customer_id
GROUP BY customers.customer_segment
ORDER BY total_revenue DESC;
```

### Result

The database calculates the actual revenue by customer segment, and the verified result is then converted into a concise natural-language response.

This demonstrates the complete flow:

```text
Business Question
       ↓
Semantic Understanding
       ↓
Dynamic SQL Generation
       ↓
SQL Validation
       ↓
Database Execution
       ↓
Verified Result
       ↓
Natural-Language Answer
```

---

## 📌 Key Design Principles

### 1. Database as the Source of Truth

Business metrics are calculated from the CustomerIQ database rather than invented by the language model.

### 2. Dynamic Querying

The AI is designed to interpret arbitrary business questions instead of relying on a fixed set of predefined queries.

### 3. Semantic Control

The semantic layer defines the available data model, business definitions, relationships, and terminology.

### 4. Read-Only SQL

Generated queries are restricted to safe analytical operations.

### 5. Separation of Responsibilities

The system separates:

```text
Business semantics
        ↓
Query planning
        ↓
SQL validation
        ↓
SQL execution
        ↓
Answer generation
```

### 6. Business-Focused Analytics

The project focuses on translating data into decisions around:

- Customer retention
- Revenue protection
- Profit protection
- Customer value
- Churn risk
- Retention prioritization

---

## 🎓 What This Project Demonstrates

CustomerIQ demonstrates practical experience across:

- Data cleaning and preparation
- Exploratory data analysis
- SQL analytics
- Customer segmentation
- RFM analysis
- Machine-learning churn prediction
- Financial risk quantification
- Power BI dashboard development
- Data storytelling
- Database design
- Semantic-layer design
- Natural-language-to-SQL systems
- LLM integration
- SQL validation and safety
- FastAPI development
- Cloud deployment
- Git/GitHub version control

The project is designed to demonstrate not only how to build analytical dashboards, but also how to build a complete analytics system where business users can move from **data → prediction → financial impact → natural-language analysis → action**.

---

## 📜 License

This project is intended as a portfolio project demonstrating data analytics, machine learning, business intelligence, and AI application development.
