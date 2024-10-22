import re
import boto3
import csv
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

def get_snapshots():
    return ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

def get_volumes():
    return dict([
        (v['VolumeId'], v)
        for v in ec2.describe_volumes()['Volumes']
    ])

def get_instances():
    reservations = ec2.describe_instances()['Reservations']
    instances = [
        instance
        for reservation in reservations
        for instance in reservation['Instances']
    ]
    return dict([
        (i['InstanceId'], i)
        for i in instances
    ])

def get_images():
    images = ec2.describe_images(Owners=['self'])['Images']
    return dict([
        (i['ImageId'], i)
        for i in images
    ])

def parse_description(description):
    regex = r"^Created by CreateImage\((.*?)\) for (.*?) "
    matches = re.finditer(regex, description, re.MULTILINE)
    for matchNum, match in enumerate(matches):
        return match.groups()
    return '', ''


def main():

    volumes = get_volumes()
    instances = get_instances()
    images = get_images()


    def volume_exists(volume_id):
        return volume_id in volumes if volume_id else ''

    def instance_exists(instance_id):
        return instance_id in instances if instance_id else ''

    def image_exists(image_id):
        return image_id in images if image_id else ''

    with open('report.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'snapshot id',
            'description',
            'started',
            'size',
            'volume',
            'volume exists',
            'instance',
            'instance exists',
            'ami',
            'ami exists'])
        for snap in get_snapshots():
            instance_id, image_id = parse_description(snap['Description'])
            writer.writerow([
                snap['SnapshotId'],
                snap['Description'],
                snap['StartTime'],
                str(snap['VolumeSize']),
                snap['VolumeId'],
                str(volume_exists(snap['VolumeId'])),
                instance_id,
                str(instance_exists(instance_id)),
                image_id,
                str(image_exists(image_id)),
            ])

if __name__ == '__main__':
    main()