# infra-aware-code-review-automation

Design Principle: Deterministic infrastructure validation before probabilistic inference

An automated, RAG-driven framework to audit AWS Glue ETL scripts for security,
performance, and compliance using Anthropic Claude 3.5 Sonnet via Amazon Bedrock.

Disclaimer: This project is a generalized reference implementation.
All names, identifiers, and configurations are illustrative.


Quick Start

1. Setup

AWS Access: Enable Anthropic Claude 3.5 Sonnet in Bedrock Model Access.

Local Env: Python 3.13+ and configured AWS CLI.

Boto3 installation or upgrade: Install boto3 on local

Bash
pip install --upgrade boto3

2. Deploy

The deploy.py script automates CloudFormation deployment, S3 seeding, and Lambda packaging.

Bash
git clone https://github.com/chhabrapooja/infra-aware-code-review-automation.git
python deploy.py


3. Run Review

Analyze all Glue Jobs associated with a specific business use-case:

Bash
python review.py <<use-case-name>>

Example:
python review.py customer


Architecture

The system follows an orchestration pattern that separates infrastructure, logic, and knowledge:

Orchestration (review.py): A local script that identifies relevant Glue jobs based on use-case and triggers the audit.

Audit Engine (AWS Lambda): A Python-based function that extracts script code from Glue and executes the RAG logic.

Knowledge Base (S3): A centralized checklist file that acts as the "ground truth" for the LLM.

Inference (AWS Bedrock): Claude 3.5 Sonnet analyzes the code against the checklist and generates a structured JSON report.


Project Structure
|—— review.py                                        # Local Orchestrator (entry point)
|—— infra/
|	    |——   cloudformation.yml                       # IAM Roles, Lambda, S3, and Sample Glue Jobs
|
|—— src/
|	    |—— raw_customer_data.py, curated_customer_data.py, raw_inventory_data.py                        # Synthetic "Bad" code for demo
| 
|—— knowledge-base/
|	     |—— checklist.md                              # RAG Ground Truth (Review Rules)
|
|——	deploy.py					                               # Boto3 Deployment Script
|—— LICENSE						                               # MIT License
|—— README.md


Technical Challenges & Solutions

RAG Precision: To avoid LLM "hallucinations," I provided a strict checklist. By passing this as context to Claude, the model is forced to evaluate code against specific organizational rules rather than generic internet standards.

Infrastructure as Code: Handled complex circular dependencies between S3 bucket creation and Lambda code zipping by building a custom Boto3 deployment orchestrator (deploy.py).

Security: Used LLMs provided by AWS bedrock for code security and data residency. Data is encrypted at rest using bucket policy. In transit data security is ensured by AWS. 

Multi-Model Evaluation: Compared Claude 3.5 Sonnet results against Amazon Nova Pro Model for cost optimization. Nova Pro fared cheaper and performant for larger contexts with a 300K token context window. However, Claude 3.5 Sonnet fared better in critical implementations for catching every possible edge case when cost is of secondary importance.


Future Roadmap

CI/CD Integration: Trigger reviews automatically on GitHub Pull Requests.


