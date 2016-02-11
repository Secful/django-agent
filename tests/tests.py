import unittest
from mock import patch, Mock
from secfuldjangoplugin import Secful, Request, Response

class TestSecfulPlugin(unittest.TestCase):
    agent_uuid = '12345'
    message_uuid = '999'
    maxDiff = None

    @patch('secfuldjangoplugin.settings', new=Mock(SECFUL_KEY='key'))
    @patch('secfuldjangoplugin.create_connection')
    @patch('secfuldjangoplugin.threading')
    def setUp(self, threading, create_conn):
        self.secful = Secful()

    def test_process_response(self):
        request = self.create_request()
        response = self.create_response()
        self.secful.process_response(request, response)

        # check queue is full
        self.secful.MAX_QUEUE_SIZE = 2
        [self.secful.queue.put(1) for _ in range(5)]
        self.secful.process_response(request, response)

    @patch('secfuldjangoplugin.threading.current_thread')
    def test_do_work(self, current_thread):
        self.secful.threads_to_sockets = {current_thread(): Mock()}
        request = self.create_request()
        message = Request(request.META,
                          request.get_full_path(),
                          request.method,
                          request.user.id,
                          request.read(),
                          self.message_uuid)
        self.secful.do_work(message)
        
        response = self.create_response()
        message = Response(response.items(),
                           response.status_code,
                           response.reason_phrase,
                           response.content,
                           self.message_uuid)
        self.secful.do_work(message)

    def test_get_request_dict(self):
        res_request_dict = {
 'messageId': self.message_uuid,
 'request': {'headers': [{'key': 'ORIGIN', 'value': 'file://'},
   {'key': 'HOST', 'value': 'localhost:8000'},
   {'key': 'CACHE-CONTROL', 'value': 'no-cache'},
   {'key': 'ACCEPT', 'value': '*/*'},
   {'key': 'ACCEPT-LANGUAGE', 'value': 'en-US'},
   {'key': 'CONTENT-ABC', 'value': '123'},
   {'key': 'USER-AGENT',
    'value': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Postman/3.2.10.1 Chrome/45.0.2454.85 Electron/0.34.3 Safari/537.36'},
   {'key': 'CONNECTION', 'value': 'keep-alive'},
   {'key': 'POSTMAN-TOKEN', 'value': '617b876d-19a7-d504-a6c6-07ae0ea6b171'},
   {'key': 'ACCEPT-ENCODING', 'value': 'gzip, deflate'},
   {'key': 'CONTENT-TYPE', 'value': 'application/json'},
   {'key': 'CONTENT-LENGTH', 'value': '582'}],
  'method': 'GET',
  'path': '/a/b/c/',
  'payload': {'glossary': {'GlossDiv': {'GlossList': {'GlossEntry': {'Abbrev': 'ISO 8879:1986',
       'Acronym': 'SGML',
       'GlossDef': {'GlossSeeAlso': ['GML', 'XML'],
        'para': 'A meta-markup language, used to create markup languages such as DocBook.'},
       'GlossSee': 'markup',
       'GlossTerm': 'Standard Generalized Markup Language',
       'ID': 'SGML',
       'SortAs': 'SGML'}},
     'title': 'S'},
    'title': 'example glossary'}},
  'version': 'HTTP/1.1'},
 'metadata': [{'key': 'user-id', 'value': '123'}],
 'userSrcIp': '127.0.0.1'}

        request = self.create_request()
        message = Request(request.META,
                          request.get_full_path(),
                          request.method,
                          request.user.id,
                          request.read(),
                          self.message_uuid)
        request_dict = self.secful.get_request_dict(message)
        request_dict.pop('companyLocalIps')
        
        self.assertDictEqual(request_dict, res_request_dict)
    
    def test_get_response_dict(self):
        res_response_dict = {'messageId': '999',
 'response': {'headers': [{'key': 'Content-Type',
    'value': 'text/html; charset=utf-8'}],
  'payload': "Hello, world. You're at the polls index.",
  'reasonMessage': 'OK',
  'statusCode': 200}}

        response = self.create_response()
        message = Response(response.items(),
                           response.status_code,
                           response.reason_phrase,
                           response.content,
                           self.message_uuid)
        response_dict = self.secful.get_response_dict(message)
        
        self.assertDictEqual(response_dict, res_response_dict)

    def create_request(self):
        request = Mock()
        request.user = Mock(id=123)
        request.get_full_path = Mock(return_value='/a/b/c/')
        request.method = 'GET'

        request.META = {'Apple_PubSub_Socket_Render': '/private/tmp/com.apple.launchd.thiBUr2jkJ/Render',
                        'CLICOLOR': '1',
                        'COLORFGBG': '7;0',
                        'CONTENT_LENGTH': '582',
                        'CONTENT_TYPE': 'application/json',
                        'DJANGO_SETTINGS_MODULE': 'djangoplugin.settings',
                        'EDITOR': 'vim',
                        'GATEWAY_INTERFACE': 'CGI/1.1',
                        'HOME': '/Users/michaelvilensky',
                        'HTTP_ACCEPT': '*/*',
                        'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
                        'HTTP_ACCEPT_LANGUAGE': 'en-US',
                        'HTTP_CACHE_CONTROL': 'no-cache',
                        'HTTP_CONNECTION': 'keep-alive',
                        'HTTP_CONTENT_ABC': '123',
                        'HTTP_HOST': 'localhost:8000',
                        'HTTP_ORIGIN': 'file://',
                        'HTTP_POSTMAN_TOKEN': '617b876d-19a7-d504-a6c6-07ae0ea6b171',
                        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Postman/3.2.10.1 Chrome/45.0.2454.85 Electron/0.34.3 Safari/537.36',
                        'ITERM_PROFILE': 'Default',
                        'ITERM_SESSION_ID': 'w0t7p0',
                        'LANG': 'en_US.UTF-8',
                        'LC_ALL': 'en_US.UTF-8',
                        'LC_CTYPE': 'UTF-8',
                        'LOGNAME': 'michaelvilensky',
                        'LS_OPTIONS': ' -F',
                        'OLDPWD': '/Users/michaelvilensky',
                        'PATH': '/Users/michaelvilensky/.rbenv/shims:/Users/michaelvilensky/.cabal/bin:/opt/local/bin:/opt/local/sbin:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Users/michaelvilensky/bin',
                        'PATH_INFO': u'/',
                        'PWD': '/Users/michaelvilensky/secful/djangoplugin',
                        'PYTHONPATH': '/Users/michaelvilensky/work/python/',
                        'PYTHONSTARTUP': '/Users/michaelvilensky/work/python/startup.py',
                        'QUERY_STRING': '',
                        'REMOTE_ADDR': '127.0.0.1',
                        'REMOTE_HOST': '',
                        'REQUEST_METHOD': 'POST',
                        'RUN_MAIN': 'true',
                        'SCRIPT_NAME': u'',
                        'SERVER_NAME': '1.0.0.127.in-addr.arpa',
                        'SERVER_PORT': '8000',
                        'SERVER_PROTOCOL': 'HTTP/1.1',
                        'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.10',
                        'SHELL': '/bin/bash',
                        'SHLVL': '1',
                        'SSH_AUTH_SOCK': '/private/tmp/com.apple.launchd.GhhfQGIYd2/Listeners',
                        'TERM': 'xterm-256color',
                        'TERM_PROGRAM': 'iTerm.app',
                        'TMPDIR': '/var/folders/2b/yzlqs7bn051cn5jx2d41m90c0000gn/T/',
                        'TZ': 'UTC',
                        'USER': 'michaelvilensky',
                        'XPC_FLAGS': '0x0',
                        'XPC_SERVICE_NAME': '0',
                        '_': '/usr/local/bin/python',
                        '__CF_USER_TEXT_ENCODING': '0x1F5:0x0:0x0',
                        'wsgi.multiprocess': False,
                        'wsgi.multithread': True,
                        'wsgi.run_once': False,
                        'wsgi.url_scheme': 'http',
                        'wsgi.version': (1, 0)}
        request.body = {
                        "glossary": {
                                    "title": "example glossary",
                                    "GlossDiv": {
                                                "title": "S",
                                                "GlossList": {
                                                            "GlossEntry": {
                                                                    "ID": "SGML",
                                                                    "SortAs": "SGML",
                                                                    "GlossTerm": "Standard Generalized Markup Language",
                                                                    "Acronym": "SGML",
                                                                    "Abbrev": "ISO 8879:1986",
                                                                    "GlossDef": {
                                                                        "para": "A meta-markup language, used to create markup languages such as DocBook.",
                                                                        "GlossSeeAlso": ["GML", "XML"]
                                                                    },
                                                                    "GlossSee": "markup"
                                                                        }
                                                            }
                                                }
                                    }
                    }
        request.read = Mock(return_value=request.body)
        return request
    
    def create_response(self):
        response = Mock()
        response.items = Mock(return_value = [('Content-Type', 'text/html; charset=utf-8')])
        response.status_code = 200
        response.reason_phrase = 'OK'
        response.content = "Hello, world. You're at the polls index."
        return response
