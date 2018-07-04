from django.conf import settings

from .models import Event

VISITOR_COOKIE_KEY = 'visitor_id'
DONT_TRACK = ['/media/', '/jsi18n/', '/static/']

def is_trackable(url):
    for path in DONT_TRACK:
        if path in url:
            return False
    return True


def get_session_id(request):
    return request.COOKIES.get(VISITOR_COOKIE_KEY, '')


def get_product_pks(products):
    if isinstance(products, (list,)):
        return [x[0].pk for x in products]
    else:
        return [products]


def report_event(visitor_id, url, headers, products=None):
    referrer = headers.get('HTTP_REFERER', None)
    user_agent = headers.get('HTTP_USER_AGENT', None)
    query_string = headers.get('QUERY_STRING', None)
    defaults = {
        'visitor_id': visitor_id,
        'url': url,
        'referrer': referrer,
        'user_agent': user_agent,
        'query_string': query_string,
        'products': products
    }
    Event.objects.create(**defaults)