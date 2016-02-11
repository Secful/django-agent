from websocket import create_connection
from django.conf import settings
import uuid
import re
import socket
import json
import time
import threading
import Queue

class Secful:
    
    MAX_QUEUE_SIZE = 50
    NUM_OF_THREADS = 5
    SOCKET_TIMEOUT = 1
    WS_SERVER_HOST = 'ws://localhost:7000'

    def __init__(self):
        try:
            self.queue = Queue.Queue(maxsize=self.MAX_QUEUE_SIZE)
            self.threads_to_sockets = {}
            self.token = getattr(settings, "SECFUL_COMPANY_ID", None)
            self.agentIdentifier = uuid.uuid4().hex
            self.start_threads()
        except:
            pass

    def start_threads(self):
        for _ in range(self.NUM_OF_THREADS):
            thread = threading.Thread(target=self.worker)
            self.connect_to_ws(thread)
            thread.start()

    ''' 
        This is the main function of the middleware 
    '''
    def process_request(self, request):
        if self.queue.qsize() < self.MAX_QUEUE_SIZE:
            self.queue.put(request)

    def worker(self):
        while True:
            try:
                request = self.queue.get()
                self.do_work(request)
                self.queue.task_done()
            except:
                pass

    def connect_to_ws(self, thread):
        try:
            ws = self.threads_to_sockets.get(thread, None)
            if ws:
                ws.close()
            token_header = ['Authorization: Bearer {}'.format(self.token)]
            self.threads_to_sockets[thread] = create_connection(self.WS_SERVER_HOST, timeout=self.SOCKET_TIMEOUT, header=token_header)
        except:
            self.threads_to_sockets[thread] = None

    def do_work(self, request):
        request_dict = Secful.get_request_dict(request, self.agentIdentifier)
        ws = self.threads_to_sockets[threading.current_thread()]
        try:
            ws.send(json.dumps(request_dict, ensure_ascii=False))
        except:
            time.sleep(60)
            self.connect_to_ws(threading.current_thread())


    @staticmethod
    def get_request_dict(request, uuid):
        headers = []
        for k, v in request.META.iteritems():
            if k.startswith('HTTP_'):
                Secful.add_key_value_to_list(k[5:].replace('_', '-'), v, headers)

        Secful.add_key_value_to_list('CONTENT-TYPE', request.META.get('CONTENT_TYPE'), headers)
        Secful.add_key_value_to_list('CONTENT-LENGTH', request.META.get('CONTENT_LENGTH'), headers)

        metadata = []
        Secful.add_key_value_to_list('user-id', request.user.id, metadata)

        http_dict = {'path': request.get_full_path() or '',
                     'version': request.META['SERVER_PROTOCOL'] or '',
                     'method': request.method or '',
                     'headers': headers,
                     'payload': request.body}

        request_dict = {'agentType': 'Python',
                        'agentVersion': '1.0',
                        'agentIdentifier': uuid,
                        'userSrcIp': request.META['REMOTE_ADDR'],
        	        'companyDstIp': socket.gethostbyname_ex(socket.gethostname())[2],
                        'metadata': metadata,
                        'http': http_dict}
        return request_dict

    @staticmethod
    def add_key_value_to_list(key, value, req_list):
        if value is not None:
            req_list.append({'key': key, 'value': value})


