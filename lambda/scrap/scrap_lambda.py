import json
import os
import boto3
import requests
import xml.etree.ElementTree as ET

from uuid import uuid4


def get_currency_data(root):
    currency_data = {}

    currency_name_elements = root.getchildren()[2].getchildren()
    for element in list(currency_name_elements):
        date = element.attrib.get("time")
        currencies = element.getchildren()
        currency_data[date] = {}
        for cube in list(currencies):
            currency = cube.attrib.get("currency")
            rate = cube.attrib.get("rate")
            currency_data[date][currency] = rate
    return currency_data


def extract_currencies():
    request_url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml?ccff4b91d2713471dadc8ccca7e8490f"
    print("REQUEST URL", request_url)
    response = requests.get(request_url)
    root = ET.fromstring(response.text)
    return get_currency_data(root=root)


def lambda_handler(event, context):
    # TODO implement
    print(event)
    
    currency = extract_currencies()

    dynamodb = boto3.resource('dynamodb')
    TABLE_NAME = os.environ['TABLE_NAME']
    table = dynamodb.Table(TABLE_NAME)

    for date, item in currency.items():
        table.put_item(Item={
                    "id": date,
                    "data": item
                }
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Scrapping process completed!')
    }