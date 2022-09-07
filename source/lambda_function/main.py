#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import os
from datetime import datetime, timedelta
import boto3
import random

print("Loading function...")
s3_bucket = os.environ.get("S3_BUCKET")
print("Working with:", s3_bucket)

datetime_format = "%Y-%m-%d-%H%M%S/"

s3_client = boto3.client("s3")
s3 = boto3.resource("s3")


def get_objects(bucket, prefix):
    result = set()

    paginator = s3_client.get_paginator("list_object_versions")
    operation_parameters = {"Bucket": bucket, "Prefix": prefix, "Delimiter": "/"}
    page_iterator = paginator.paginate(**operation_parameters)

    for page in page_iterator:
        for obj in page["CommonPrefixes"]:
            result.add(obj["Prefix"].replace(prefix, ""))
    return result


def list_to_datetime(object_list):
    datetime_list = []
    for i in object_list:
        datetime_list.append(datetime.strptime(i, datetime_format))
    return datetime_list


def filter_date(datetime_list):
    datetime_list.sort()
    date7daysago = datetime_list[-1] - timedelta(days=7)
    date365daysago = datetime_list[-1] - timedelta(days=365)
    date = datetime_list[-1].date()

    filtered = []
    for i in datetime_list:
        if i.date() <= date365daysago.date():
            filtered.append(i)
        if date365daysago.date() < i.date() <= date7daysago.date():
            if i.date() != date:
                date = i.date()
            else:
                filtered.append(i)
    return filtered


def datetime_to_list(datetime_list, prefix):
    object_list = []
    for i in datetime_list:
        object_list.append(prefix + i.strftime(datetime_format))
    return object_list


def delete_objects(object_list):
    bucket = s3.Bucket(s3_bucket)
    for i in object_list:
        print("Deleting path:", i)
        bucket.object_versions.filter(Prefix=i).delete()


def lambda_handler(event, context):
    """Main Lambda function
    Args:
        event (dict): AWS Cloudwatch Scheduled Event
        context (object): AWS running context
    Returns:
        None
    """
    path_prefix = ["circlet/", "vcs-dfs/"]

    filtered_candidats = []
    for prefix in path_prefix:
        object_list = get_objects(s3_bucket, prefix)
        datetime_list = list_to_datetime(object_list)
        filtered_datetile_list = filter_date(datetime_list)
        filtered_object_list = datetime_to_list(filtered_datetile_list, prefix)
        filtered_candidats += filtered_object_list
    print("Cleanup candidates:")
    print(filtered_candidats)
    random.shuffle(filtered_candidats)
    delete_objects(filtered_candidats)


if __name__ == "__main__":
    lambda_handler({}, "")
