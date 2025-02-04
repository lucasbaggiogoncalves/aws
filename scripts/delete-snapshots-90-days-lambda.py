import boto3
from datetime import datetime, timedelta, timezone

################################################################################
# Define the number of days to keep
days_to_keep = 90
################################################################################

session = boto3.Session()
ec2 = session.resource('ec2')

def list_older_snapshots(days):
    older_snapshots = []
    days_ago = datetime.now(timezone.utc) - timedelta(days=days)
    
    for snapshot in ec2.snapshots.filter(OwnerIds=['self']):
        if snapshot.start_time < days_ago:
            older_snapshots.append(snapshot.id)

    return older_snapshots

def lambda_handler(event, context):

    older_snapshots = list_older_snapshots(days_to_keep)

    removed_snapshots = []
    for snapshot_id in older_snapshots:
        try:
            ec2.Snapshot(snapshot_id).delete()
            removed_snapshots.append(snapshot_id)
        except Exception as e:
            print(f'Erro ao remover snapshot id: {snapshot_id}, {e}')

    message = (f'Processamento concluido. {len(removed_snapshots)} '
               f'snapshot(s) removido(s) / IDs: ' + ', '.join(removed_snapshots)
              ) if removed_snapshots else 'Nenhum snapshot removido'

    return {
        'statusCode': 200,
        'body': message
    }