import beg 

beg.default_ssl_context.load_verify_locations('badssl-ca.cer')
result = beg.get('http://google.com', params={'foo':'bar'})

print(result)