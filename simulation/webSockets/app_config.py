import os

flaskHttpAppConfig = {}
flaskHttpAppConfig['USE_HTTPS'] = False
flaskHttpAppConfig['GEMBER_HTTPS_KEYFILE'] = '/private/etc/ssl/localhost/localhost.key'
flaskHttpAppConfig['GEMBER_HTTPS_CERTFILE'] = '/private/etc/ssl/localhost/localhost.crt'
flaskHttpAppConfig['GEMBER_BIND_HOST'] = '127.0.0.1'
flaskHttpAppConfig['GEMBER_PORT'] = 8443
flaskHttpAppConfig['SECRET_KEY'] = os.urandom(24)
flaskHttpAppConfig["ALLOW_THREADING"] = False
flaskHttpAppConfig['DEBUG_APP'] = True

ssl_args = {}
if flaskHttpAppConfig.get('USE_HTTPS') and flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE') and flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE'):
    ssl_args = {
        'keyfile': flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE')
    }
