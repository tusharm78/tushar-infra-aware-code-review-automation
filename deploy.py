import boto3
import sys
import time
import os
import botocore

# Configuration
STACK_NAME = "tushar-test-stack"
TEMPLATE_FILE = "infra/cloudformation.yml"
REGION = "us-east-1"  # Change to your region

cf_client = boto3.client("cloudformation", region_name=REGION)
s3_client = boto3.client("s3", region_name=REGION)


def deploy_stack():
    print(f"--- Starting Deployment for {STACK_NAME} ---")

    with open(TEMPLATE_FILE, "r") as f:
        template_body = f.read()

    params = {
        "StackName": STACK_NAME,
        "TemplateBody": template_body,
        "Capabilities": ["CAPABILITY_NAMED_IAM"],
    }

    try:
        cf_client.describe_stacks(StackName=STACK_NAME)
        print("Stack already exists, updating")

        # Create or Update the stack
        cf_client.update_stack(**params)
        print("Waiting for stack creation to complete... (this takes ~3 mins)")
        waiter = cf_client.get_waiter("stack_create_complete")
        # waiter.wait(StackName=STACK_NAME)
        print("Stack updated successfully!")

    except botocore.exceptions.ClientError as e:
        if (
            e.response["Error"]["Code"] == "ValidationError"
            and "does not exist" in e.response["Error"]["Message"]
        ):
            print("Stack does not exist. Creating new stack...")
            cf_client.create_stack(**params)
            waiter = cf_client.get_waiter("stack_create_complete")
        else:
            raise e

    try:
        print("Waiting for stack operation to complete...")
        waiter.wait(StackName=STACK_NAME)
        print("Stack is ready!")

    except botocore.exceptions.ClientError as e:
        if "No updates are to be performed" in str(e):
            print(
                "No changes detected in YAML. Infrastructure is already up to date."
            )
        else:
            raise e


def get_bucket_name():
    paginator = cf_client.get_paginator("list_stack_resources")
    for page in paginator.paginate(StackName=STACK_NAME):
        for resource in page["StackResourceSummaries"]:
            if resource["ResourceType"] == "AWS::S3::Bucket":
                return resource["PhysicalResourceId"]
    return None


def upload_assets(bucket_name):
    print(f"--- Uploading Assets to S3 Bucket: {bucket_name} ---")

    files_to_upload = {
        "knowledge-base/checklist.md": "scripts/checklist.md",
        "src/raw_customer_data.py": "scripts/raw_customer_data.py",
        "src/raw_inventory_data.py": "scripts/raw_inventory_data.py",
        "src/curated_customer_data.py": "scripts/curated_customer_data.py",
    }

    for local_file, s3_key in files_to_upload.items():
        if os.path.exists(local_file):
            s3_client.upload_file(local_file, bucket_name, s3_key)
            print(f"Uploaded: {s3_key}")
        else:
            print(f"Warning: {local_file} not found. Skipping.")


if __name__ == "__main__":
    deploy_stack()
    bucket = get_bucket_name()

    if bucket:
        upload_assets(bucket)
        print(
            "\nDeployment complete! You can now run "
            "'python review.py <your use case name>'"
        )
    else:
        print("Error: Could not find S3BucketName in CloudFormation stack.")

