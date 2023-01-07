#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint
import pathlib

import googleapiclient.discovery
import google.auth
import google.oauth2.service_account as service_account

#
# Use Google Service Account - See https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html#module-google.oauth2.service_account
#
if pathlib.Path('service-credentials.json').exists():
    credentials = service_account.Credentials.from_service_account_file(filename='service-credentials.json')
    project = os.getenv('GOOGLE_CLOUD_PROJECT')
else:
    credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name, bucket):

    # Configure the machine
    machine_type = "zones/%s/machineTypes/f1-micro" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'vm1-startup-script.sh'), 'r').read()
    service_credentials = open(
        os.path.join(
            os.path.dirname(__file__), 'service-credentials.json'), 'r').read()
    vm2_startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'vm2-startup-script.sh'), 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                "initializeParams": {
                "sourceSnapshot": "global/snapshots/snapshot-1",
                }
            }
        ],

        # Specify a network interface with NAT to access public internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'text',
                'value': image_caption
            }, {
                'key': 'bucket',
                'value': bucket
            }, {
                'key': 'vm2-startup-script',
                'value': vm2_startup_script
            }, {
                'key': 'service-credentials',
                'value': service_credentials
            }, {
                'key': 'project',
                'value': project
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]


# [START delete_instance]
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
# [END delete_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]

# [START run]
def main(project, bucket, zone, instance_name, instance_id, wait=True):

    instance_name = [f'lab5-part3-{instance_id}']
    try:
        for i in range(len(instance_name)):
            print(f'Creating instance {instance_name[i]}.')
            operation = create_instance(service, project, zone, instance_name[i], bucket)
            wait_for_operation(service, project, zone, operation['name'])
    finally:
        if wait:
            input()

        print('Deleting instance.')

        for i in range(len(instance_name)):    
            operation = delete_instance(service, project, zone, instance_name[i])
            wait_for_operation(service, project, zone, operation['name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--project_id',
        default=project if len(project) > 0 else 'snappy-attic-365421',
        help='Your Google Cloud project ID.')    
    parser.add_argument(
        '--bucket_name',
        default='lab5_cloud',
        help='Your Google Cloud bucket name.')
    parser.add_argument(
        '--zone',
        default='us-west1-b',
        help='Compute Engine zone to deploy to.')
    parser.add_argument(
        '--name', default='lab5-part3', help='New instance name.')
    parser.add_argument(
        '--instance-id', default='1', help='New instance id. Options are 1 or 2')

    args = parser.parse_args()

    main(args.project_id, args.bucket_name, args.zone, args.name, args.instance_id)

# [END run]
