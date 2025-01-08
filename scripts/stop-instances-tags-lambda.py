import boto3

tags = [
    {
        'Key': 'turn-off-hours',
        'Value': 'true'
    }
]

def get_instances_to_stop(ec2_client):

    ec2_filters = tags
    response = ec2_client.describe_instances(Filters=ec2_filters)
    instances_to_stop = []

    return [
        instance['InstanceId']
        for reservation in response['Reservations']
        for instance in reservation['Instances']
    ]

def stop_instances(ec2_client,instances):

    if instances:
        ec2_client.stop_instances(InstanceIds=instances)
        print(f"Instâncias paradas: {instances}")
    

def lambda_handler(event, context):

    ec2_client = boto3.client('ec2')
    instances_to_stop = get_instances_to_stop(ec2_client)

    if instances_to_stop:

        stop_instances(ec2_client,instances_to_stop)
        
    return {
        'statusCode': 200,
        'body': (
            f"Processamento concluído. {'Instâncias paradas: ' + str(len(instances_to_stop)) if instances_to_stop else 'Sem instâncias para parar'}"
        )
    }