import sys
import boto3
import json
import multiprocessing
from pathlib import Path


def get_stack_name(job_name):
    if "customer_data" in job_name:
        return ("tushar-test-stack", "tushar-test-stack")
    elif "sales_data" in job_name:
        return ("tushar-sales-stack", "tushar-sales-stack")
    elif "product_data" in job_name:
        return ("tushar-product-stack", "tushar-product-stack")
    return (None, None)


def is_resource_deployed_thru_cft(resource, stack_name):
    cfn = boto3.client("cloudformation")
    paginator = cfn.get_paginator("list_stack_resources")
    for page in paginator.paginate(StackName=stack_name):
        for r in page["StackResourceSummaries"]:
            if r["PhysicalResourceId"] == resource:
                return True
    return False


def review_code_and_infra(pickle_element):
    glue_job_name = pickle_element[0]
    use_case = pickle_element[1]
    glue = boto3.client("glue")
    llm_run_flag = True
    job_exists_flag = True
    print(f"Starting AWS Glue Job Peer Review for {glue_job_name} ")
    try:
        exists = glue.get_job(JobName=glue_job_name)
        infra_review_text = """================================================================================
        \t\t\t\t\t\t\tInfra Review\n================================================================================\nGlue Job Exists"""
    except:
        print(f"{glue_job_name} job doesn't exist, please check input")
        job_exists_flag = False

    if job_exists_flag == True:
        crawler_name = glue_job_name.replace("gluejob", "crawler")  # update according to your Infra naming standards here
        job_stack_name, crawler_stack_name = get_stack_name(glue_job_name)

        if job_stack_name:
            if is_resource_deployed_thru_cft(glue_job_name, job_stack_name):
                infra_review_text += (
                    f"\n- Resource: Glue Job ({glue_job_name})"
                    f"\n  Status: Deployed"
                    f"\n  Provisioning Source: IaC (CloudFormation: {job_stack_name})"
                    f"\n  Compliance: Project standards met"
                )
            else:
                infra_review_text += (
                    f"\n\n- Resource: Glue Job ({glue_job_name})"
                    f"\n  Status: Not Deployed"
                    f"\n  Provisioning Source: Not traceable"
                    f"\n  Compliance: Project standards not met"
                )
                llm_run_flag = False
        else:
            infra_review_text += "\njob stack not found, check input"
            llm_run_flag = False

        try:
            exists = glue.get_crawler(Name=crawler_name)["Crawler"]
            infra_review_text += "\n\nCrawler Exists"
            crawler_exists_flag = True
        except:
            infra_review_text += f"\n\nCrawler Doesn't Exist"
            infra_review_text += f"\n{crawler_name} Expected"
            crawler_exists_flag = False

        if crawler_stack_name and crawler_exists_flag:
            if is_resource_deployed_thru_cft(crawler_name, crawler_stack_name):
                infra_review_text += (
                    f"\n- Resource: Crawler ({crawler_name})"
                    f"\n  Status: Deployed"
                    f"\n  Provisioning Source: IaC (CloudFormation: {crawler_stack_name})"
                    f"\n  Compliance: Project standards met"
                )
            else:
                infra_review_text += (
                    f"\n- Resource: Crawler ({crawler_name})"
                    f"\n  Status: Not Deployed"
                    f"\n  Provisioning Source: Not traceable"
                    f"\n  Compliance: Project standards not met"
                )
        else:
            if crawler_exists_flag:
                infra_review_text += "\ncrawler stack not found, check input"
                infra_review_text += "\n Compliance: Project standards not met"
            else:
                infra_review_text += f"\n- Compliance: Project standards not met"

    infra_review_text += """\n================================================================================
    \t\t\t\t\t\t\tInfra Review Completed\n================================================================================"""


    folder_name = Path(f"{use_case}_peer review")
    folder_name.mkdir(exist_ok=True)

    file_name = f"{folder_name}/{glue_job_name}_peer_review.md"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(infra_review_text)

    if llm_run_flag:
        lambda_client = boto3.client("lambda")
        response = lambda_client.invoke(
            FunctionName="pooja-test-lambda",
            Payload=json.dumps({"gluejob_name": glue_job_name})
        )
        payload = json.loads(response["Payload"].read())
        review_text = payload["body"]["peer_review"]
    else:
        review_text = "\nglue job isn't deployed through cft, code review skipped"

    code_review_header = """\n\n\n================================================================================
    \t\t\t\t\t\t\tCode Review\n================================================================================"""

    code_review_footer = """\n================================================================================
    \t\t\t\t\t\t\tCode Review Completed\n================================================================================"""

    with open(file_name, "a", encoding="utf-8") as f:
        f.write(code_review_header)
        f.write(review_text)
        f.write(code_review_footer)


if __name__ == "__main__":
    job_list = []
    glue = boto3.client("glue")

    if len(sys.argv) != 2:
        print("usage : python review.py <use case name like customer>")
        sys.exit(1)

    use_case_id = sys.argv[1]
    print("scanning for jobs for given use case")

    paginator = glue.get_paginator("get_jobs")
    for page in paginator.paginate():
        for job in page['Jobs']:
            if (job['Name'].startswith('') and use_case_id in job['Name']):
                job_list.append((job['Name'], use_case_id))

    if len(job_list) == 0:
        print("no jobs found for this use case. Please check input")
        sys.exit(1)
    else:
        print("Reviewing")
        for i in job_list:
            print(i)

    with multiprocessing.Pool() as pool:
        pool.map(review_code_and_infra, job_list)

    print("\nPeer review completed successfully!")
    print(f"Output folder : {use_case_id}")
    print("====================================================================================================================\n")
