from django.conf import settings

from .models import Event

SESSION_ID = 'sessionid'
DONT_TRACK = ['/media/', '/jsi18n/', '/static/']

def is_trackable(url):
    for path in DONT_TRACK:
        if path in url:
            return False
    return True


def get_session_id(request):
    return request.COOKIES.get(SESSION_ID, '')


def report_event(session_id, url, headers):
    referrer = headers.get('HTTP_REFERER', None)
    user_agent = headers.get('HTTP_USER_AGENT', None)
    query_string = headers.get('QUERY_STRING', None)
    defaults = {
        'session_id': session_id,
        'url': url,
        'referrer': referrer,
        'user_agent': user_agent,
        'query_string': query_string
    }
    Event.objects.create(**defaults)