from requests import Response

def response_info(response: Response):
    info = {
        'request_method': response.request.method,
        'request-url': response.request.url,
        'response-status-code': response.status_code,
    }

    if response.request.method not in {'DELETE', 'HEAD', 'OPTION'}:
        info['content-type'] = response.headers['content-type']
        info['response-content'] = response.json()
    else:
        info['response-content'] = response.text

    return info

