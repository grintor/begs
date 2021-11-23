[![PyPI version](https://badge.fury.io/py/begs.svg)](https://badge.fury.io/py/begs)

# begs
#### A rewrite of the famous requests library with better defaults and certificate handling



`begs` is a from-scratch rewrite of the python `request` library. It is API-compatible with `requests`, but has some improvements.

Why you should consider using begs over requests:

- It is much lighter. While `requests` (314 KB) depends on `urllib3` (660 KB), `certifi` (257 KB), `idna` (467 KB) and `charset-normalizer` (220 KB), `begs` has no dependencies and is less than 20 KB, making it a great choice for use in packages where size matters.

- The `requests` library does not support using the built-in system certificate store - relying instead on the hard-coded ssl certificates in the `certifi` library. This makes distribution to systems located behind SSL-proxy firewalls with self-signed certificates a nightmare. `begs` supports the system certificate store by default, and makes appending additional certificates to the trusted CA list a breeze. 

- The `requests` library has a long-standing issue of allowing users to shoot themselves in the foot by not providing a default timeout. `begs` has a very reasonable 30 second timeout which can be adjusted as-needed.

- `begs` also supports various retry options, and will even automatically retry in situations where it can be determined that a retry would be safe and idempotent (such as a 503 response to a POST, or a 500 response to a GET)

  

"begs" is a play on words - a more aggressive form of "requests". (to beg vs to request) because by default, the begs library will automatically retry certain requests if they fail for certain reasons. More on that below.



##### Getting Started:

```python
import begs # or even "import begs as requests"

begs.get('http://microsoft.com')
```

It's that easy!



##### More Examples:

```python
import begs

# auto-decode json
req = begs.post('https://httpbin.org/post', data={'foo': 'bar'}, params={'me': 'you'})
print(req.json())

# get the response body as text
req = begs.get('https://httpbin.org/ip')
print(req.text)

# get the resonse headers as a dict
req = begs.get('https://google.com')
print(req.headers)
```



##### Adding a trusted Certificate Authority:

```python
import begs

# this will set a ssl context for all future begs requests
begs.default_ssl_context.load_verify_locations('badssl-ca.cer')

# would normally raise an ssl exception, but won't now.
result = begs.get('https://untrusted-root.badssl.com/')

#################################################################################################

import ssl
custom_context = ssl.create_default_context() # you can also specify your own ssl context per-request
result = begs.get('https://untrusted-root.badssl.com/', ssl_context=custom_context)

```



##### Retries:

```python
import begs

# this request will fail after 4 attempts (0 seconds, 1 second, 2 seconds, 4 seconds)
# getaddrinfo failed exception
begs.get('http://something-that-doesnt-exist.internal', retries=3, retry_delay=1, retry_backoff=2, force_retry=True)
```

by default retries=1 and force_retry=False which means it will instantly retry up to one time for any safe and idempotent request (like a 500 response to a GET, a timeout to a GET, a 503 response to a POST, etc). You can alter the retry options per-request as above, or you can set the defaults at the module-level like so:

```python
import begs

begs.default_retries = 3
begs.default_retry_delay = 1
begs.default_retry_backoff = 2

begs.get('http://something-that-doesnt-exist.internal')
```



##### Timeouts:

The default timeout is 30 seconds, but it can be altered at the module-level or per-request

```python
import begs

begs.default_timeout = 60

begs.get('http://something-that-doesnt-exist.internal', timeout=45)
```



##### TODO:

Begs implements the most important things for working with most REST APIs, but is not feature-complete. The following major features remain unimplemented for now:

- Cookies
- AUTH: Basic, Digest
- File Uploads (multipart/form-data)
- Proxies
