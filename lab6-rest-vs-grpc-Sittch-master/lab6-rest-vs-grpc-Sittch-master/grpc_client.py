import random
import requests
import json,base64
import time,random
import sys

import grpc
import service_pb2
import service_pb2_grpc



def service_add(stub, debug):
    sum = stub.add(service_pb2.addMsg(a=5, b=10))
    if debug:
        print(f"Found {sum}")
    return sum

def service_dot(stub, debug):
    v1 = []
    v2 = []
    for n in range(100):
        v1.append(random.random())
        v2.append(random.random())

    dot = stub.dotproduct(service_pb2.dotProductMsg(a=v1, b=v2))
    if debug:
        print(f"Found {dot}")

def service_jsonimage(stub, debug):
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    img_encoded = base64.b64encode(img)
    request = service_pb2.jsonImageMsg(img=img_encoded)
    size = stub.jsonimage(request)
    if debug:
        print(f"Found {size}")

def service_rawimage(stub, debug):
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    request = service_pb2.rawImageMsg(img=img)
    size = stub.rawimage(request)
    if debug:
        print(f"Found {size}")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.ServerStub(channel)
        print("-------------- Add --------------")
        service_add(stub, 1, 2)
        print("-------------- Dotproduct --------------")
        service_dot(stub)
        print("-------------- JsonImg --------------")
        service_jsonimage(stub)
        print("-------------- RawImg --------------")
        service_rawimage(stub)


if __name__ == '__main__':

    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} <server ip> <cmd> <reps>")
        print(f"where <cmd> is one of add, rawImage, sum or jsonImage")
        print(f"and <reps> is the integer number of repititions for measurement")
        print(f"last parameter <debug> 1 for print, 0 for no")

    host = sys.argv[1]
    cmd = sys.argv[2]
    reps = int(sys.argv[3])
    debug = int(sys.argv[4])

    addr = f"{host}:50051"
    print(f"Running {reps} reps against {addr}")

    with grpc.insecure_channel(addr) as channel:
        stub = service_pb2_grpc.ServerStub(channel)

        if cmd == 'rawImage':
            start = time.perf_counter()
            for x in range(reps):
                service_rawimage(stub, debug)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'add':
            start = time.perf_counter()
            for x in range(reps):
                service_add(stub, debug)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'jsonImage':
            start = time.perf_counter()
            for x in range(reps):
                service_jsonimage(stub, debug)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        elif cmd == 'dotProduct':
            start = time.perf_counter()
            for x in range(reps):
                service_dot(stub, debug)
            delta = ((time.perf_counter() - start)/reps)*1000
            print("Took", delta, "ms per operation")
        else:
            print("Unknown option", cmd)