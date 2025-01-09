# Requires the JSON_BUCKET_NAME environment variable to be set on lambda

import boto3
import json
import os

def read_csv_from_bucket (s3_client,bucket_name, key):
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    csv_data = response['Body'].read().decode('utf-8')
    return csv_data

def convert_csv_to_json(csv_data):
    lines = csv_data.splitlines()
    headers = lines[0].lstrip('\ufeff').split(';')
    json_list = []

    for line in lines[1:]:
        values = line.split(';')
        record = dict(zip(headers, values))
        json_list.append(record)
    
    json_data = (json.dumps(json_list, ensure_ascii=False, indent=4))
    return json_data

def send_json_to_bucket(s3_client, bucket_name, key, json_data):
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=json_data)

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    csv_bucket_name = event['Records'][0]['s3']['bucket']['name']
    csv_key = event['Records'][0]['s3']['object']['key']
    csv_data = read_csv_from_bucket(s3, csv_bucket_name, csv_key)

    json_data = convert_csv_to_json(csv_data)
    json_bucket_destination = os.getenv('JSON_BUCKET_NAME')
    send_json_to_bucket(s3, json_bucket_destination, csv_key + '.json', json_data)

    return {
        'statusCode': 200,
        'body': json_data
    }