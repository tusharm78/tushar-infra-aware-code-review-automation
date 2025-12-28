import sys
import boto3
from awsglue.utils import getResolvedOptions


# ERROR 1: Hardcoded credentials (Security Risk)
ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


# ERROR 2: Hardcoded S3 Bucket (Lack of Portability)
S3_BUCKET = "my-personal-dev-bucket-123"


def main():
    print("Starting Glue Job...")  # ERROR 3: Using print() instead of logging

    s3 = boto3.client('s3')

    try:
        # ERROR 4: No error handling for specific Boto3 exceptions
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        for obj in response.get('Contents', []):
            print(f"Found file: {obj['Key']}")

    except Exception as e:
        # ERROR 5: Bare exception or generic error message
        print("Something went wrong.")


if __name__ == "__main__":
    main()
