import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.functional import SimpleLazyObject
from django.utils.translation import get_language
from django_countries.fields import Country
from django.utils.crypto import get_random_string

from . import analytics
from . import tracking
from ..discount.models import Sale
from .utils import get_client_ip, get_country_by_ip, get_currency_for_country
from .utils.taxes import get_taxes_for_country

logger = logging.getLogger(__name__)


def google_analytics(get_response):
    """Report a page view to Google Analytics."""
    def middleware(request):
        client_id = analytics.get_client_id(request)
        path = request.path
        language = get_language()
        headers = request.META
        try:
            analytics.report_view(
                client_id, path=path, language=language, headers=headers)
        except Exception:
            logger.exception('Unable to update analytics')
        return get_response(request)
    return middleware


def tracking_system(get_response):
    def middleware(request):
        session_id = tracking.get_session_id(request)
        path = request.path
        headers = request.META
        try:
            if tracking.is_trackable(path):
                tracking.report_event(session_id, path, headers)
        except Exception:
            logger.exception('Unable to update tracking system')
        return get_response(request)
    return middleware


def tracking_session(get_response):
    def middleware(request):
        try:
            if request.COOKIES.get('visitor_id', '') == '':
                visitor_id = get_random_string(length=38)
                response = get_response(request)
                response.set_cookie('visitor_id', visitor_id, max_age=52560000)
                return response
        except Exception:
            logger.exception('Unable to set visitor_id')
        return get_response(request)
    return middleware


def discounts(get_response):
    """Assign active discounts to `request.discounts`."""
    def middleware(request):
        discounts = Sale.objects.prefetch_related('products', 'categories')
        request.discounts = discounts
        return get_response(request)

    return middleware


def country(get_response):
    """Detect the user's country and assign it to `request.country`."""
    def middleware(request):
        client_ip = get_client_ip(request)
        if client_ip:
            request.country = get_country_by_ip(client_ip)
        if not request.country:
            request.country = Country(settings.DEFAULT_COUNTRY)
        return get_response(request)

    return middleware


def currency(get_response):
    """Take a country and assign a matching currency to `request.currency`."""
    def middleware(request):
        if hasattr(request, 'country') and request.country is not None:
            request.currency = get_currency_for_country(request.country)
        else:
            request.currency = settings.DEFAULT_CURRENCY
        return get_response(request)

    return middleware


def site(get_response):
    """Clear the Sites cache and assign the current site to `request.site`.

    By default django.contrib.sites caches Site instances at the module
    level. This leads to problems when updating Site instances, as it's
    required to restart all application servers in order to invalidate
    the cache. Using this middleware solves this problem.
    """
    def middleware(request):
        Site.objects.clear_cache()
        request.site = Site.objects.get_current()
        return get_response(request)

    return middleware


def taxes(get_response):
    """Assign tax rates for default country to `request.taxes`."""
    def middleware(request):
        if settings.VATLAYER_ACCESS_KEY:
            request.taxes = SimpleLazyObject(lambda: get_taxes_for_country(
                request.country))
        else:
            request.taxes = None
        return get_response(request)

    return middleware
