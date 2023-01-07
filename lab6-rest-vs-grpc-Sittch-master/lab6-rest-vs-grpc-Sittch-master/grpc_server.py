from concurrent import futures
import logging
import base64
import io
from PIL import Image

import grpc
import service_pb2
import service_pb2_grpc


class ServerServicer(service_pb2_grpc.ServerServicer):
    """implement"""

    def add(self, request, context):
        return service_pb2.addReply(sum = request.a + request.b)

    def dotproduct(self, request, context):
        v1 = request.a
        v2 = request.b
        if (len(v1) != len(v2)):
            return service_pb2.dotProductReply(dotproduct = 0)
        sum = 0
        for i in range(len(v1)):
            sum += v1[i] * v2[i]
        return service_pb2.dotProductReply(dotproduct = sum)

    def rawimage(self, request, context):
        imgBytes = request.img
        imgIO = io.BytesIO(imgBytes)
        img = Image.open(imgIO)
        response = service_pb2.imageReply(width=img.size[0], height=img.size[1])
        return response

    def jsonimage(self, request, context):
        data = request.img
        imgBytes = base64.b64decode(data)
        imgIO = io.BytesIO(imgBytes)
        img = Image.open(imgIO)
        response = service_pb2.imageReply(width=img.size[0], height=img.size[1])
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ServerServicer_to_server(
        ServerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()