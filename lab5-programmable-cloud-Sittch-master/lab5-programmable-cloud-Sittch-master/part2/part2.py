import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth

credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

fire_wall_name = "allow-5000"

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
                "initializeParams": {
                "sourceSnapshot": "global/snapshots/snapshot-1",
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
            "items":[fire_wall_name]
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
        "name": fire_wall_name,
        "sourceRanges": [
            "0.0.0.0/0" 
        ],
        "targetTags": [
            fire_wall_name
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
        firewall_exists = service.firewalls().get(project=project, firewall=fire_wall_name).execute() # check if firewall already set up
        if firewall_exists:
            print("The firewall you are setting already exist.")
            print()
    except: # if not, setup a firewall and add it to firewall. execute it
        firewall_body = firewall_Setup(project=project)        
        service.firewalls().insert(project=project, body=firewall_body).execute() # execute the firewall here
# [END add_firewall_node]


# [START run]
def main(project, bucket, zone, instance_name, wait=True):

    temp = [0,1,2]
    t = [0,1,2,3]
    timelist = []
    instance_name = ['lab5-part2a','lab5-part2b','lab5-part2c']
    # operation = [0,1,2]
    for i in range(len(temp)):
        print(f'Creating instance {temp[i]}.')
        time.sleep(30)
        t[i] = time.time()
        operation = create_instance(service, project, zone, instance_name[i], bucket)
        # wait_for_operation(service, project, zone, operation['name'])
        wait_for_operation(service, project, zone, operation['name'])
        t[i+1] = time.time()
        diff = t[i+1] - t[i]
        timelist.append(diff)

    if wait:
        input()

    print('Deleting instance.')

    for i in range(len(instance_name)):    
        operation = delete_instance(service, project, zone, instance_name[i])
        wait_for_operation(service, project, zone, operation['name'])

    print(timelist)
    with open('TIMING.md','w') as f:
        for item in timelist:
            f.write("%s\n" % item)


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
        '--name', default='lab5-part2', help='New instance name.')

    args = parser.parse_args()

    main(args.project_id, args.bucket_name, args.zone, args.name)

# [END run]
