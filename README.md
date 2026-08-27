# CustomerIQ — AI-Powered Customer Intelligence & Retention Analytics

CustomerIQ is an end-to-end customer retention analytics solution that combines **SQL, Python, Machine Learning, Power BI, FastAPI, and Generative AI** to identify customers at risk of churn, quantify financial exposure, prioritize retention actions, and answer customer intelligence questions using natural language.

🔗 **Live AI Demo:** https://customeriq-ai.onrender.com/

---

## 📌 Project Overview

Customer churn is not just a customer-retention problem — it is a revenue and profitability problem.

CustomerIQ transforms customer transaction and interaction data into actionable retention intelligence by answering four key business questions:

- **Who is likely to churn?**
- **Which customers should we prioritize?**
- **How much revenue and profit are at risk?**
- **What should the business do next?**

The solution combines predictive analytics with an AI-powered natural-language interface so decision-makers can move from dashboards to questions and actionable insights.

---

## 🎯 Business Objectives

The project was designed to:

- Identify customers with a high probability of churn
- Segment customers using RFM analysis
- Quantify expected revenue and profit at risk
- Prioritize customers for retention campaigns
- Recommend retention actions based on customer risk
- Provide executive-level insights through Power BI
- Enable natural-language customer intelligence through AI

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

### Key retention insight

The **Hibernating** RFM segment represents the primary retention focus:

- **230 customers**
- **132 predicted churners**
- **57.39% predicted churn rate**

This means the segment accounts for the overwhelming majority of predicted churners and represents the clearest concentration of retention risk.

---

## 🧠 Predictive Analytics

A machine-learning churn model was used to estimate each customer's probability of churn.

The resulting customer-level dataset contains predictive and business-oriented metrics including:

- Churn probability
- Predicted churn
- Churn risk
- Customer value
- Expected revenue at risk
- Expected profit at risk
- Retention score
- Retention priority
- Recommended retention action

The model outputs are then used throughout the Power BI dashboard and AI query engine.

---

## 👥 RFM Customer Segmentation

Customers were segmented using **Recency, Frequency, and Monetary (RFM)** analysis.

Customer segments include:

- Champions
- Loyal Customers
- High Value
- At Risk High Value
- Potential Loyalists
- Recent Customers
- Needs Attention
- Hibernating

RFM segmentation provides additional context around predicted churn and helps translate model outputs into actionable customer groups.

---

## 📈 Power BI Dashboard

The Power BI dashboard is structured into three pages.

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
- Recommended retention actions
- High-risk customer identification

### Page 3 — CustomerIQ AI

An AI entry point that allows users to ask natural-language questions about:

- Customer churn
- Customer risk
- Revenue exposure
- Retention priorities
- Individual customers
- RFM segments

---

## 🤖 AI-Powered Customer Intelligence

CustomerIQ includes a locally developed AI application rather than relying solely on a generic chatbot.

### Architecture

```text
                    Customer Data
                         │
                         ▼
                  Data Preparation
                         │
                         ▼
                 Churn Prediction
                         │
                         ▼
              CustomerIQ Scored Data
                    ┌────┴────┐
                    │         │
                    ▼         ▼
                 Power BI   AI Query Engine
                    │         │
                    │         ▼
                    │       FastAPI
                    │         │
                    │         ▼
                    │    Ollama Cloud
                    │         │
                    │         ▼
                    │      gpt-oss:20b
                    │         │
                    └────┬────┘
                         ▼
                 Business Decisions
