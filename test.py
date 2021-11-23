import begs 

begs.default_ssl_context.load_verify_locations('badssl-ca.cer')
result = begs.get('https://untrusted-root.badssl.com/')

print(result)