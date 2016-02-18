import boto3

def main(event, context):
  client = boto3.client(u'ecs')

  inspect_clusters = [u'staging1']

  for cluster in inspect_clusters:
    resp = client.list_container_instances(
      cluster=cluster
    )

    instances = resp[u'containerInstanceArns']

    try:
      nxt_tok = resp[u'nextToken']

      while True:
        resp = client.list_container_instances(
          cluster=cluster,
          nextToken=nxt_tok
        )

        instances += resp[u'containerInstanceArns']
        nxt_tok = resp[u'nextToken']
    except KeyError:
      pass

    resp = client.describe_container_instances(
      cluster=cluster,
      containerInstances=instances
    )

    ec2 = boto3.resource('ec2')
    client = boto3.client('autoscaling')

    for inst in resp[u'containerInstances']:
      if not inst['agentConnected']:
        I = ec2.Instance(id=inst[u'ec2InstanceId'])

        autoscalegroup = filter(lambda k: k['Key'] == u'aws:autoscaling:groupName', I.tags)[0]['Value']

        print I.id, u': ', autoscalegroup
