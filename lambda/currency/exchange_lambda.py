from __future__ import print_function

import json
import decimal
import os
import boto3
from datetime import timedelta, datetime

from aws_cdk.aws_kms import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']


def get_weekdays(start_date=None):
    if start_date:
        week_no = start_date.weekday()
    else:
        week_no = datetime.today().weekday()
    if week_no == 0:
        present_day = start_date
        current_date = present_day.strftime("%Y-%m-%d")
        last_day = present_day - timedelta(days=1)
        last_date = last_day.strftime("%Y-%m-%d")
    elif week_no == 6:
        present_day = start_date
        current_date = present_day.strftime("%Y-%m-%d")
        last_day = present_day - timedelta(days=1)
        last_date = last_day.strftime("%Y-%m-%d")
    elif week_no == 5:
        present_day = start_date
        current_date = present_day.strftime("%Y-%m-%d")
        last_day = present_day - timedelta(days=1)
        last_date = last_day.strftime("%Y-%m-%d")
    else:
        current_date = start_date.strftime('%Y-%m-%d')
        last_day = start_date - timedelta(days=1)
        last_date = last_day.strftime("%Y-%m-%d")

    return current_date, last_date


def get_currency_rates(today_currency, lastday_currency):
    """
    Extracts Comparison of the currency rate between current and previous currency differences.

    { "currency_code": {"today": rate, "difference": today rate - previous_rate}},
    { "currency_code": {"today": rate, "difference": today rate - previous_rate}},
    """
    return {
            x: {
                "today": float(today_currency["data"][x]),
                "difference": round(float(today_currency["data"][x]) - float(lastday_currency["data"][x]), 3)
            }
            for x, y in today_currency["data"].items()
    }


def lambda_handler(event, context):

    current_date, last_date = get_weekdays()
    
    table = dynamodb.Table(TABLE_NAME)
    # Scan items in table for current, previous date
    try:
        today_currency = table.query(
            KeyConditionExpression=Key('date').eq(current_date)
        )
        last_date_currency = table.query(
            KeyConditionExpression=Key('date').eq(last_date)
        )

        response = get_currency_rates(today_currency, last_date_currency)

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        # print item of the table - see CloudWatch logs
        for i in response['Items']:
            print(json.dumps(i))

    return {
        'response': response, 
        'statusCode': 200,
    }
