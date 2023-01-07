import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth

credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

firewall_id = "allow-5000"

# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name, bucket):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/f1-micro" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
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
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
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

        'tags':{
            "items":[firewall_id]
        },

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

# [START firewall_setup to set the firewall node we want]
def firewall_Setup(project):
    firewall_body = {
        "name": firewall_id,
        "sourceRanges": [
            "0.0.0.0/0" 
        ],
        "targetTags": [
            firewall_id
        ],
        "allowed": [
            {
            "IPProtocol": "tcp",
            "ports": [
                "5000"
            ]
            }
        ]
    }
    return firewall_body
# [END firewall setup]

# [START add_firewall_node to add the firewall node we just setup into the firewall list]
def add_firewall_node(project):
    # add firewall node to the firewalls list
    try:
        firewall_exists = service.firewalls().get(project=project, firewall=firewall_id).execute() # check if firewall already set up
        if firewall_exists:
            print("The firewall you are setting already exist.")
            print()
    except: # if not, setup a firewall and add it to firewall. execute it
        firewall_body = firewall_Setup(project=project)        
        service.firewalls().insert(project=project, body=firewall_body).execute() # execute the firewall here
# [END add_firewall_node]


# [START run]
def main(project, bucket, zone, instance_name, wait=True):

    print('Creating instance.')

    operation = create_instance(service, project, zone, instance_name, bucket)
    wait_for_operation(service, project, zone, operation['name'])

    add_firewall_node(project=project)    

    instances = list_instances(service, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])

    print("""
Instance created.
It will take a minute or two for the instance to complete work.
Check this URL: http://storage.googleapis.com/{}/output.png
Once the image is uploaded press enter to delete the instance.
""".format(bucket))

    if wait:
        input()

    print('Deleting instance.')

    operation = delete_instance(service, project, zone, instance_name)
    wait_for_operation(service, project, zone, operation['name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--project_id',
        default='snappy-attic-365421',
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
        '--name', default='lab5-part1', help='New instance name.')

    args = parser.parse_args()

    main(args.project_id, args.bucket_name, args.zone, args.name)
# [END run]
