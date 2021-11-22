import urllib.request, ssl, time
import json as jsonlib
from pprint import pformat
from cgi import parse_header
from urllib.parse import urlencode

VERSION = 0.1
ALWAYS_SAFE_RETRY_STATUSES = [413, 425, 429, 503]
IDEMPOTENT_SAFE_RETRY_STATUSES = [408, 409, 500, 502, 503, 504]
SAFE_VERBS = ['GET', 'HEAD', 'OPTIONS', 'TRACE']

default_ssl_context = ssl.create_default_context()
default_timeout = 30
default_retries = 1
default_retry_delay = 0.01
default_retry_backoff = 2

def request(verb, url, **kwargs):

    supported_kwargs = [
        'body', 'headers', 'timeout', 'ssl_context', 'data', 'json', 'params', 'retries', 'retry_delay', 'retry_backoff', 'force_retry'
    ]

    for kwarg in kwargs:
        if kwarg not in supported_kwargs:
            raise NotImplementedError(f"unknown kwarg: {kwarg}")

    body           = kwargs.get('body', b'')
    headers        = kwargs.get('headers', {})
    timeout        = kwargs.get('timeout', default_timeout)
    ssl_context    = kwargs.get('ssl_context', default_ssl_context)
    json           = kwargs.get('json', None)
    retries        = kwargs.get('retries', default_retries)
    retry_delay    = kwargs.get('retry_delay', default_retry_delay)
    retry_backoff  = kwargs.get('retry_backoff', default_retry_backoff)
    force_retry    = kwargs.get('force_retry', False)
    data           = kwargs.get('data', None)
    params         = kwargs.get('params', None)

    verb = verb.upper() # from 'post' to POST, etc...
    headers = {k.lower(): v for k, v in headers.items()} # lowercase the header keys

    if 'user-agent' not in headers.keys():
        headers['user-agent'] = f'Mozilla/5.0 (compatible; t2t_request/{VERSION}; +http://www.tier2.tech/)'

    if json:
        request_body = jsonlib.dumps(json).encode('UTF-8')
        headers['content-type'] = 'application/json'

    if isinstance(data, str):
        if not 'content-type' in headers:
            headers['content-type'] = 'text/plain'
        request_body = data.encode('UTF-8')

    if isinstance(data, dict):
        headers['content-type'] = 'application/x-www-form-urlencoded'
        request_body = urlencode(data).encode('UTF-8')

    if params:
        url = f"{url}?{urlencode(params)}"

    if not data:
        request_body = b''
    else:
        assert isinstance(data, (dict, str)), "data param must be a dict or a string"

    req_class = urllib.request.Request(url=url, data=request_body, headers=headers, method=verb)

    request_attempts = 0
    attempts_remaining = retries + 1
    while attempts_remaining:
        try:
            attempts_remaining -= 1
            request_attempts += 1
            with urllib.request.urlopen(
                req_class,
                timeout=timeout,
                context=ssl_context
            ) as response:
                status = response.status
                header_tuples = response.getheaders()
                response_body = response.read()
                url = response.url

            break # success, don't retry.

        except urllib.error.HTTPError as e:
            status = e.code
            header_tuples = e.headers.items()
            response_body = e.read()
            url = e.url

            safe_to_retry = False

            if status in ALWAYS_SAFE_RETRY_STATUSES:
                safe_to_retry = True

            if verb in SAFE_VERBS and status in IDEMPOTENT_SAFE_RETRY_STATUSES:
                safe_to_retry = True

            if not safe_to_retry and not force_retry:
                break  # don't retry.

        except Exception as e:
            if attempts_remaining == 0: # last try, and we failed.
                raise(e)

        time.sleep(retry_delay)
        retry_delay *= retry_backoff
        
        
    class ReturnedResponse(object):
        def json(self):
            return jsonlib.loads(self.text)

        def __repr__(self):
            return pformat({
                'url': self.url,
                'status': self.status,
                'ok': self.ok,
                'headers': dict,
                'headers_multi': dict,
                'text': str,
                'body': bytes,
                'attempts': self.attempts
            }, compact=True)
    
    ReturnedResponse.ok = False
    if status < 400:
        ReturnedResponse.ok = True

    ReturnedResponse.status = status
    ReturnedResponse.attempts = request_attempts
    ReturnedResponse.body = response_body
    ReturnedResponse.url = url

    ReturnedResponse.status_code = status # backwards compatible with 'requests'
    ReturnedResponse.content = response_body # backwards compatible with 'requests'

    headers = {}
    headers_multi = {}
    for header_name, value in header_tuples:
        header_name = header_name.lower()
        headers[header_name] = value
        if header_name not in headers_multi:
            headers_multi[header_name] = [value]
        else:
            headers_multi[header_name].append(value)
    ReturnedResponse.headers = headers
    ReturnedResponse.headers_multi = headers_multi

    content_type = parse_header(headers['content-type'])

    for field in content_type:
        if isinstance(field, dict):
            dict_field_lowercase = {k.lower(): v for k, v in field.items()}
            if 'charset' in dict_field_lowercase:
                try:
                    ReturnedResponse.encoding = dict_field_lowercase['charset'].lower()
                    ReturnedResponse.text = response_body.decode(dict_field_lowercase['charset'])
                except LookupError:
                    pass # the server returned and unknown encoding
    if not hasattr(ReturnedResponse, 'text'): # the server didn't tell us the encoding or it was unknown
        try:
            ReturnedResponse.text = response_body.decode('UTF-8') # just a guess
            ReturnedResponse.encoding = 'utf-8'
        except Exception:
            ReturnedResponse.text = None
            ReturnedResponse.encoding = None

    return ReturnedResponse()

def get(url, **kwargs):
    return request('get', url, **kwargs)

def head(url, **kwargs):
    return request('head', url, **kwargs)

def options(url, **kwargs):
    return request('options', url, **kwargs)
    
def trace(url, **kwargs):
    return request('trace', url, **kwargs)
    
def put(url, **kwargs):
    return request('put', url, **kwargs)
    
def delete(url, **kwargs):
    return request('delete', url, **kwargs)
    
def post(url, **kwargs):
    return request('post', url, **kwargs)
