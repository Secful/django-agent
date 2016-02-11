from websocket import create_connection
from django.conf import settings
import uuid
import socket
import json
import time
import threading
import Queue

class Request(object):
    Type = 'request'

    def __init__(self, META, full_path, method, user_id, payload, uuid):
        self.META = META
        self.full_path = full_path
        self.method = method
        self.user_id = user_id
        self.payload = payload
        self.uuid = uuid


class Response(object):
    Type = 'response'

    def __init__(self, items, status_code, reason_phrase, payload, uuid):
        self.items = items
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.payload = payload
        self.uuid = uuid


class Secful(object):
    
    MAX_QUEUE_SIZE = 50
    NUM_OF_THREADS = 5
    SOCKET_TIMEOUT = 1

    def __init__(self):
        try:
            self.queue = Queue.Queue(maxsize=self.MAX_QUEUE_SIZE)
            self.threads_to_sockets = {}
            self.token = getattr(settings, "SECFUL_KEY", None)
            self.ws_server_host = getattr(settings, "SECFUL_HOST", None)
            self.agent_identifier = uuid.uuid4().hex
            self.start_threads()
        except:
            pass

    def start_threads(self):
        for _ in range(self.NUM_OF_THREADS):
            thread = threading.Thread(target=self.worker)
            self.connect_to_ws(thread)
            thread.start()
    
    def process_request(self, request):
        request._secful_message_uuid = uuid.uuid4().hex
        try:
            data = request.body
        except Exception:
            data = ''
        copied_request = Request(request.META,
                                 request.get_full_path(),
                                 request.method,
                                 request.user.id if request.user else None,
                                 data,
                                 request._secful_message_uuid)
        try:
            self.queue.put_nowait(copied_request)
        except:
            pass

    def process_response(self, request, response):
        message_uuid = getattr(request, '_secful_message_uuid', None)
        copied_response = Response(response.items(),
                                   response.status_code,
                                   response.reason_phrase,
                                   response.content,
                                   message_uuid)
        try:
            self.queue.put_nowait(copied_response)
        except:
            pass
        return response
            
    def worker(self):
        while True:
            try:
                message = self.queue.get()
                self.do_work(message)
                self.queue.task_done()
            except:
                pass

    def connect_to_ws(self, thread):
        try:
            ws = self.threads_to_sockets.get(thread, None)
            if ws:
                ws.close()

            headers = {'Agent-Type: Python',
                       'Agent-Version: 1.0',
                       'Agent-Identifier: {}'.format(self.agent_identifier),
                       'Authorization: Bearer {}'.format(self.token)}

            self.threads_to_sockets[thread] = create_connection(self.ws_server_host, timeout=self.SOCKET_TIMEOUT, header=headers)
        except:
            self.threads_to_sockets[thread] = None

    def do_work(self, message):
        message_dict = self.parse_message(message)
        ws = self.threads_to_sockets[threading.current_thread()]
        try:
            ws.send(json.dumps(message_dict, ensure_ascii=False))
        except:
            time.sleep(60)
            self.connect_to_ws(threading.current_thread())

    def parse_message(self, message):
        return self.PARSER_DICT[message.Type](message)

    @staticmethod
    def get_response_dict(response):
        headers = []
        for k, v in response.items:
            Secful.add_key_value_to_list(k, v, headers)

        http_dict = {'statusCode': response.status_code,
                     'reasonMessage': response.reason_phrase,
                     'headers': headers,
                     'payload': response.payload}

        response_dict = {'messageId': response.uuid,
                         response.Type: http_dict}
        return response_dict

    @staticmethod
    def get_request_dict(request):
        headers = []
        for k, v in request.META.iteritems():
            if k.startswith('HTTP_'):
                Secful.add_key_value_to_list(k[5:].replace('_', '-'), v, headers)

        Secful.add_key_value_to_list('CONTENT-TYPE', request.META.get('CONTENT_TYPE'), headers)
        Secful.add_key_value_to_list('CONTENT-LENGTH', request.META.get('CONTENT_LENGTH'), headers)

        metadata = []
        Secful.add_key_value_to_list('user-id', request.user_id, metadata)

        http_dict = {'path': request.full_path or '',
                     'version': request.META['SERVER_PROTOCOL'] or '',
                     'method': request.method or '',
                     'headers': headers,
                     'payload': request.payload}

        request_dict = {'messageId': request.uuid,
                        'userSrcIp': request.META['REMOTE_ADDR'],
                        'companyLocalIps': socket.gethostbyname_ex(socket.gethostname())[2],
                        'metadata': metadata,
                        request.Type: http_dict}
        return request_dict

    PARSER_DICT = {Request.Type: get_request_dict.__func__,
                   Response.Type: get_response_dict.__func__}

    @staticmethod
    def add_key_value_to_list(key, value, req_list):
        if value is not None:
            req_list.append({'key': str(key), 'value': str(value)})


