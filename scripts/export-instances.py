import boto3
import csv

ec2 = boto3.client('ec2')

instances = ec2.describe_instances()

tag_keys = set()
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        if 'Tags' in instance:
            for tag in instance['Tags']:
                tag_keys.add(tag['Key'])

with open('instances_with_tags.csv', 'w', newline='') as csvfile:
    fieldnames = ['InstanceId', 'InstanceType', 'State', 'Zone', 'PrivateIpAddress', 'PrivateDnsName', 'PublicDnsName'] + list(tag_keys)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            row = {
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'Zone': instance['Placement']['AvailabilityZone'],
                'PrivateIpAddress': instance['PrivateIpAddress'],
                'PrivateDnsName': instance['PrivateDnsName'],
                'PublicDnsName': instance['PublicDnsName'],
            }

            if 'Tags' in instance:
                for tag in instance['Tags']:
                    row[tag['Key']] = tag['Value']

            writer.writerow(row)
