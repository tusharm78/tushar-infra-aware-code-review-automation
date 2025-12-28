import sys
import boto3
from awsglue.utils import getResolvedOptions


args = getResolvedOptions(sys.argv, ['ACCESS_KEY', 'SECRET_KEY', 'S3_BUCKET1', 'S3_BUCKET2'])
access_key = args['ACCESS_KEY']
secret_key = args['SECRET_KEY']

s3_bucket1 = args['S3_BUCKET1']
s3_bucket2 = args['S3_BUCKET2']


def main():
    print("Starting Glue Job...")

    s3 = boto3.client('s3')

    # ERROR : No error handling
    response = s3.list_objects_v2(s3_bucket)
    for obj in response.get('Contents', []):
        print(f"Found file: {obj['Key']}")

        response = s3.list_objects_v2(s3_bucket1)
    for obj in response.get('Contents', []):
        print(f"Found file: {obj['Key']}")

        response = s3.list_objects_v2(s3_bucket2)


if __name__ == "__main__":
    main()
