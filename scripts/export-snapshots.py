import csv
import boto3

def write_to_csv(snapshot_list):
    with open('snapshots.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Description', 'Creation date', 'Size', 'Volume ID', 'Instance ID', 'Instance Name', 'Exists'])
        for snapshot in snapshot_list:
            writer.writerow([snapshot['SnapshotId'], snapshot['Description'], snapshot['StartTime'], 
                             snapshot['VolumeSize'], snapshot['VolumeId'], snapshot.get('InstanceId', ''), 
                             snapshot.get('InstanceName', ''), snapshot.get('Exists', '')])

def get_all_snapshots():
    session = boto3.Session()
    ec2 = session.resource('ec2')
    
    snapshot_list = []
    for snapshot in ec2.snapshots.filter(OwnerIds=['self']):
        instance_id = ''
        instance_name = ''
        exists = ''

        try:
            volume = ec2.Volume(snapshot.volume_id)
            exists = True if volume.state != 'deleted' else False

            attachments = volume.attachments
            if attachments:
                instance_id = attachments[0]['InstanceId']
                instance = ec2.Instance(instance_id)
                instance_name = [tag['Value'] for tag in instance.tags if tag['Key']=='Name'][0]
            
        except Exception as e:
            print('Exception: ', e)
            exists = False
        
        snapshot_list.append({'SnapshotId': snapshot.snapshot_id, 
                              'Description': snapshot.description, 
                              'StartTime': snapshot.start_time, 
                              'VolumeSize': snapshot.volume_size,
                              'VolumeExists': exists,
                              'VolumeId': snapshot.volume_id,
                              'InstanceId': instance_id,
                              'InstanceName': instance_name,})
      
    return snapshot_list

def main():
    
    snapshot_list = get_all_snapshots() # default region
    write_to_csv(snapshot_list)

if __name__ == "__main__":
    main()
