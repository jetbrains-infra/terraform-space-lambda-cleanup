#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import os
import random
from datetime import datetime, timedelta

import boto3

print("Loading function...")
S3_BUCKET = os.environ.get("S3_BUCKET")
print("Working with:", S3_BUCKET)

DATETIME_FORMAT = "%Y-%m-%d-%H%M%S/"

s3_client = boto3.client("s3")
s3 = boto3.resource("s3")


def get_objects(bucket, prefix):
    """Get object from S3 bucket"""
    result = set()

    paginator = s3_client.get_paginator("list_object_versions")
    operation_parameters = {"Bucket": bucket, "Prefix": prefix, "Delimiter": "/"}
    page_iterator = paginator.paginate(**operation_parameters)

    for page in page_iterator:
        for obj in page.get("CommonPrefixes", []):
            result.add(obj["Prefix"].replace(prefix, ""))
    return result


def list_to_datetime(object_list):
    """Convert list"""
    datetime_list = []
    for i in object_list:
        datetime_list.append(datetime.strptime(i, DATETIME_FORMAT))
    return datetime_list


def filter_date(datetime_list):
    """Filter data list"""
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
    """Convert list to object of list"""
    object_list = []
    for i in datetime_list:
        object_list.append(prefix + i.strftime(DATETIME_FORMAT))
    return object_list


def delete_objects(object_list):
    """Cleanup S3 bucket"""
    bucket = s3.Bucket(S3_BUCKET)
    for i in object_list:
        print("Deleting path:", i)
        bucket.object_versions.filter(Prefix=i).delete()


def lambda_handler(event, context):  # pylint: disable=W0613
    """Main Lambda function
    Args:
        event (dict): AWS Cloudwatch Scheduled Event
        context (object): AWS running context
    Returns:
        None
    """
    path_prefix = [
        "circlet/",
        "vcs-dfs/",
        "circlet-prod-62-app-es-backup/",
        "circlet-prod-audit-es-backup/",
    ]

    filtered_candidats = []
    for prefix in path_prefix:
        object_list = get_objects(S3_BUCKET, prefix)
        if len(object_list) == 0:
            continue
        datetime_list = list_to_datetime(object_list)
        filtered_datetile_list = filter_date(datetime_list)
        filtered_object_list = datetime_to_list(filtered_datetile_list, prefix)
        filtered_candidats += filtered_object_list
    print("Cleanup candidates:")
    print(filtered_candidats)
    random.shuffle(filtered_candidats)
    delete_objects(filtered_candidats)


if __name__ == "__main__":
    lambda_handler({}, {})
