import json

from django.contrib import messages
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import pgettext_lazy
from impersonate.views import impersonate as orig_impersonate

from ..account.models import User
from ..dashboard.views import staff_member_required
from ..product.utils import (products_for_homepage, get_product_list_context,
        products_with_details)
from ..page.utils import pages_visible_to_user
from ..product.utils.availability import products_with_availability
from ..product.filters import SimpleFilter
from ..seo.schema.webpage import get_webpage_schema


def home(request):
    products = products_for_homepage()[:8]
    products = products_with_availability(
        products, discounts=request.discounts, taxes=request.taxes,
        local_currency=request.currency)
    webpage_schema = get_webpage_schema(request)
    return TemplateResponse(
        request, 'home.html', {
            'parent': None,
            'products': products,
            'webpage_schema': json.dumps(webpage_schema)})

def arrivals(request):
    products = products_with_details(user=request.user).order_by(
        '-created_at')
    product_filter = SimpleFilter(request.GET, queryset=products)
    ctx = get_product_list_context(request, product_filter)
    new_arrivals_page = get_object_or_404(
        pages_visible_to_user(user=request.user).filter(
            slug='new-arrivals'))
    request.META['HTTP_PRODUCTS'] = ctx['products']
    ctx.update({'page':new_arrivals_page})
    return TemplateResponse(request, 'collection/arrivals.html', ctx)



@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')


def impersonate(request, uid):
    response = orig_impersonate(request, uid)
    if request.session.modified:
        msg = pgettext_lazy(
            'Impersonation message',
            'You are now logged as {}'.format(User.objects.get(pk=uid)))
        messages.success(request, msg)
    return response


def handle_404(request, exception=None):
    return TemplateResponse(request, '404.html', status=404)


def manifest(request):
    return TemplateResponse(
        request, 'manifest.json', content_type='application/json')
