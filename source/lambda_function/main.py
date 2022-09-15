#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import os
import random
import re
from datetime import datetime, timedelta

import boto3
from dateutil.parser import parse

print("Loading function...")
S3_BUCKET = os.environ.get("S3_BUCKET")
print("Working with:", S3_BUCKET)

DATETIME_FORMAT = "%Y-%m-%d-%H%M%S"

s3_client = boto3.client("s3")
s3 = boto3.resource("s3")


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def get_prefixes(bucket, prefix=""):
    """Get object from S3 bucket"""
    result = []
    paginator = s3_client.get_paginator("list_object_versions")
    operation_parameters = {"Bucket": bucket, "Prefix": prefix, "Delimiter": "/"}
    page_iterator = paginator.paginate(**operation_parameters)

    for page in page_iterator:
        for obj in page.get("CommonPrefixes", []):
            path = obj["Prefix"].replace(prefix, "")
            if is_date(path):
                result.append(prefix + path)
            else:
                result.extend(get_prefixes(bucket, path))
    return result


def list_to_datetime(object_list):
    """Convert list"""
    datetime_list = []
    for i in object_list:
        datetime_string = re.compile("^.*\/(.*)\/$").search(i).group(1)
        datetime_list.append(
            {"path": i, "datetime": datetime.strptime(datetime_string, DATETIME_FORMAT)}
        )
    return datetime_list


def filter_date(datetime_list):
    datetime_list = sorted(datetime_list, key=lambda d: d["path"])
    """Filter data list"""
    date7daysago = datetime_list[-1]["datetime"] - timedelta(days=7)
    date365daysago = datetime_list[-1]["datetime"] - timedelta(days=365)
    date = datetime_list[-1]["datetime"].date()

    filtered = []
    for i in datetime_list:
        if i["datetime"].date() <= date365daysago.date():
            filtered.append(i)
        if date365daysago.date() < i["datetime"].date() <= date7daysago.date():
            if i["datetime"].date() == date:
                filtered.append(i)
            else:
                date = i["datetime"].date()
    return filtered


def delete_objects(object_list):
    """Cleanup S3 bucket"""
    bucket = s3.Bucket(S3_BUCKET)
    for i in object_list:
        print("Deleting path:", i["path"])
        bucket.object_versions.filter(Prefix=i["path"]).delete()


def lambda_handler(event, context):  # pylint: disable=W0613
    """Main Lambda function
    Args:
        event (dict): AWS Cloudwatch Scheduled Event
        context (object): AWS running context
    Returns:
        None
    """

    prefix_list = get_prefixes(S3_BUCKET)

    datetime_list = list_to_datetime(prefix_list)
    filtered_prefix_list = filter_date(datetime_list)
    print("Cleanup candidates:")
    for i in filtered_prefix_list:
        print(i["path"])
    random.shuffle(filtered_prefix_list)
    delete_objects(filtered_prefix_list)


if __name__ == "__main__":
    lambda_handler({}, {})
