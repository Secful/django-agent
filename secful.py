from websocket import create_connection
import re
import socket
import json
import time
import threading
import Queue

class Secful:
    
    MAX_QUEUE_SIZE = 50
    NUM_OF_THREADS = 5
    WS_SERVER_HOST = 'ws://localhost:7000'

    def __init__(self):
        try:
            self.queue = Queue.Queue(maxsize=self.MAX_QUEUE_SIZE)
            self.threads_to_sockets = {}
            self.start_threads()
        except:
            pass

    def start_threads(self):
        for i in range(self.NUM_OF_THREADS):
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
            self.threads_to_sockets[thread] = create_connection(self.WS_SERVER_HOST)
        except:
            self.threads_to_sockets[thread] = None

    def do_work(self, request):
        request_dict = Secful.get_request_dict(request)
        ws = self.threads_to_sockets[threading.current_thread()]
        try:
            ws.send(json.dumps(request_dict, ensure_ascii=False))
        except:
            time.sleep(60)
            self.connect_to_ws(threading.current_thread())


    @staticmethod
    def get_request_dict(request):
        #import pudb; pudb.set_trace()
        headers = [{'key': k, 'value': v} for k,v in request.META.iteritems() 
                    if re.match('HTTP_.+|CONTENT_.+', k)]
        metadata = [{'key': 'user-id', 'value': request.user.id}]

        http_dict = {'path': request.get_full_path(),
                     'version': request.META['SERVER_PROTOCOL'],
                     'method': request.method,
                     'headers': headers,
                     'payload': request.body}

        request_dict = {'agentType': 'Python',
                        'agentVersion': '1.0',
                        'agentIdentifier': '12345',
                        'userSrcIp': request.META['REMOTE_ADDR'],
        	        'companyDstIp': socket.gethostbyname_ex(socket.gethostname())[2],
                        'metada': metadata,
                        'http': http_dict}
        return request_dict


