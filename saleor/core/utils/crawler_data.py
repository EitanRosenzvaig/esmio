import itertools
import os
import random
import unicodedata
import urllib.request as req
import urllib.parse as urlparse
from socket import timeout

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.core.files import File
from faker.providers import BaseProvider
from django.template.defaultfilters import slugify
from django_countries.fields import Country
from prices import Money

from ...core.utils.mongo_reader import MongoReader
from ...core.utils.mapper import get_category
from ...core.utils.text import strip_html_and_truncate
from ...menu.models import Menu
from ...page.models import Page
from ...product.models import (
    AttributeChoiceValue, Category, Product, ProductAttribute,
    ProductImage, ProductType, ProductVariant)
from ...product.thumbnails import create_product_thumbnails
from ...product.utils.attributes import get_name_from_attributes
from ...shipping.models import ANY_COUNTRY, ShippingMethod

from re import sub
from decimal import Decimal

# For debugg mode
from pdb import set_trace as bp
from bs4 import BeautifulSoup
from random import shuffle

NA_IMAGE_PATH = r'saleor/static/placeholders/na_image.png'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def full_mongo_import(placeholder_dir):
    mongo = MongoReader()
    brands = mongo.get_all_brands()
    shuffle(brands)
    for brand in brands:
        image_directory = os.path.join(placeholder_dir, brand)
        for item in mongo.get_all_products_from_brand(brand):
        # try:
            if item['sizes']:
                product, product_type = create_product(item)
                for size in item['sizes']:
                    if not '.' in size:
                        size = size + '.0'
                    create_size_variant(product, size)
                if 'image_urls' in item and len(item['image_urls']) > 0:
                    if type(item['image_urls']) is list:
                        urls = item['image_urls']
                    else:
                        urls = [item['image_urls']]
                    for product_image_url in urls:
                        if not product_image_url.startswith('http'):
                            product_image_url = 'http://' + product_image_url
                        create_product_image(product, image_directory, product_image_url)
                yield 'Product Added'
        # except Exception as e:
        #     yield 'Error adding product: ' + str(e)


def get_product_type(name):
    return ProductType.objects.filter(name=name)[0]


def get_category_object(item):
    name = get_category(item)
    print(name)
    return Category.objects.filter(name=name)[0]


def create_product(item):
    print(item)
    product_type = get_product_type('Calzado')
    brand = get_brand_name(product_type, item['brand'])
    category = get_category_object(item)
    description = item['description']
    name = item['title']
    vendor_url = item['url']
    price = Decimal(item['price'])
    defaults = {
        'product_type': product_type,
        'category': category,
        'name': name,
        'price': price,
        'brand': brand,
        'vendor_url': vendor_url,
        'description': description,
        'seo_description': description[:300],
        'seo_title': name[:70]
        }
    return Product.objects.create(**defaults), product_type


def get_brand_name(product_type, brand):
    brand_attribute = product_type.product_attributes.filter(slug='brand')[0]
    value = brand_attribute.values.filter(slug=brand)[0]
    return value.name

def create_size_variant(product, size):
    defaults = {
        'product': product,
        'quantity': 1,
        'cost_price': 1,
        'quantity_allocated': 0}
    size_variant = product.product_type.variant_attributes.filter(slug='size')[0]
    size_variants = size_variant.values.filter(name=size)
    if len(size_variants) > 0:
        size_variant_option = size_variants[0]
        sku = '%s-%s-%s' % (product.pk, size_variant.pk, size_variant_option.pk)
        defaults.update(attributes={size_variant.pk:size_variant_option.pk}, sku=sku)
        variant = ProductVariant(**defaults)
        if variant.attributes:
            variant.name = get_name_from_attributes(variant)
        variant.save()


def create_product_image(product, placeholder_dir, url):
    image = get_image(placeholder_dir, url)
    product_image = ProductImage(product=product, image=image)
    product_image.save()
    create_product_thumbnails.delay(product_image.pk)
    return product_image


def get_image(image_dir, url):
    image_name = str(hash(url)) + '.jpg'
    file_path = os.path.join(image_dir, image_name)
    if not os.path.isfile(file_path):
        f = open(file_path, 'wb')
        # Fix wrongly encoded URL strings:
        url = urlparse.urlsplit(url)
        url = list(url)
        url[2] = urlparse.quote(url[2])
        url = urlparse.urlunsplit(url)
        try:
            request = req.Request(url, headers=HEADERS)
            f.write(req.urlopen(request, timeout=10).read())
        except timeout:
            print('socket timed out - URL %s', url)
            file_path = NA_IMAGE_PATH
        except:
            print('get image error')
            file_path = NA_IMAGE_PATH
        f.close()

    return File(open(file_path, 'rb'))