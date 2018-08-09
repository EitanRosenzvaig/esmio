import logging
import os
import urllib.request as req
import urllib.parse as urlparse
import mimetypes
from socket import timeout

import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files import File
from django.template.defaultfilters import slugify
from django.utils import timezone

from ...core.utils.mongo_reader import MongoReader
from ...core.utils.mapper import get_category
from ...core.utils.text import strip_html_and_truncate
from ...product.models import (
    AttributeChoiceValue, Category, Product, ProductAttribute,
    ProductImage, ProductType, ProductVariant)
from ...product.thumbnails import create_product_thumbnails
from ...product.utils.attributes import get_name_from_attributes

from prices import Money
from money_parser import price_dec

# For debugg mode
from pdb import set_trace as bp
from random import shuffle

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('import_logger')

NA_IMAGE_PATH = r'products/saleor/static/placeholders/na_image.png'
VALID_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg']

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

BRAND_REORDER = {
               'sofimartire': [2,0,1,3,4],
               'viauno': [2,0,1,3,4],
               'benditopie': [1,0,2],
               'clarabarcelo': [2,0,1,3,4],
               'heyas': [2,0,1,3,4]
                }

STORAGE_SESSION = boto3.session.Session()
STORAGE_CLIENT = STORAGE_SESSION.client('s3',
                    region_name='nyc3',
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)
STORAGE_BUCKET = settings.AWS_MEDIA_BUCKET_NAME

def full_mongo_import(placeholder_dir):
    logger.info('Starting MongoReader')
    mongo = MongoReader()
    brands = mongo.get_all_brands()
    logger.info('Total brands from Mongo: %s', len(brands))
    shuffle(brands)
    for brand in brands:
        logger.info('Starting Import of %s', brand)
        image_directory = os.path.join(placeholder_dir, brand)
        brand_items = mongo.get_all_valid_products_from_brand(brand)
        # Eliminate all items that dont exist anymore (obs: dont exist != not in stock)
        delete_removed_items_from_brand(brand_items, brand)
        for item in brand_items:
            try:
                if product_exists(item):
                    product = update_product(item)
                else:
                    product = create_product(item)
                create_or_update_size_variants(product, item['sizes'])
                create_or_update_images(product, item['image_urls'], brand, image_directory)
            except Exception:
                logger.error('Failed to update or create product', exc_info=True)
                raise
    brand_finished = '%s complete!' % brand
    logger.info(brand_finished)            
    yield brand_finished

def delete_removed_items_from_brand(brand_items, brand):
    all_urls = list()
    for item in brand_items:
        all_urls.append(item['url'])
    if len(all_urls) > 0:
        brand = get_brand_name(brand)
        products_to_delete = Product.objects.filter(brand=brand).exclude(vendor_url__in=all_urls)
        logger.info('Deleting a total of %s items from database', products_to_delete.count())
        products_to_delete.delete()
        logger.info('Products deleted')

def product_exists(item):
    return Product.objects.filter(vendor_url = item['url']).exists()

def parse_item(item):
    category = get_category_object(item)
    description = item['description']
    name = item['title']
    try:
        price = Money(price_dec(str(item['price'])), settings.DEFAULT_CURRENCY)
    except Exception:
        if 'price' in item:
            logger.error('Failed to parse price %s', item['price'], exc_info=True)
        else:
            logger.error('Price parsing error', exc_info=True)
        raise
    result = {
        'category_id': category.pk,
        'price': price,
        'name': name,
        'description': description,
        'seo_description': description[:300],
        'seo_title': name[:70]
    }
    return result

def update_product(item):
    product = Product.objects.get(vendor_url=item['url'])
    parsed_fields = parse_item(item)
    # <= checks if dict is contained in another dict
    if not parsed_fields.items() <= product.__dict__.items():
        logger.info('Updating product info of %s', item['url'])
        product.__dict__.update(parsed_fields)
        product.updated_at = timezone.now()
        product.save()
    return product

def create_product(item):
    logger.info('Creating product %s', item['url'])
    product_type = get_product_type('Calzado')
    brand = get_brand_name(item['brand'])
    attributes = get_product_attributes(product_type, item)
    vendor_url = item['url']
    parsed_fields = parse_item(item)
    defaults = {
        'product_type': product_type,
        'brand': brand,
        'attributes': attributes,
        'vendor_url': vendor_url
        }
    defaults.update(parsed_fields)
    return Product.objects.create(**defaults)

def get_product_type(name):
    return ProductType.objects.get(name=name)

def get_category_object(item):
    name = get_category(item)
    return Category.objects.get(name=name)

def get_brand_name(brand_slug):
    brand_attribute = ProductAttribute.objects.get(slug='brand')
    brand_choice = AttributeChoiceValue.objects.get(attribute_id = brand_attribute.pk,
                                                    slug = brand_slug)
    return brand_choice.name

def get_product_attributes(product_type, item):
    brand = item['brand']
    brand_attribute = product_type.product_attributes.get(slug='brand')
    value = brand_attribute.values.get(slug=brand)
    return {brand_attribute.pk:value.pk}

def parse_url(url):
    # Fix wrongly encoded URL strings:
    if not url.startswith('http'):
        url = 'https://' + url
    url = urlparse.urlsplit(url)
    url = list(url)
    url[2] = urlparse.quote(url[2])
    url = urlparse.urlunsplit(url)
    return url

def format_image_urls(image_urls, brand):
    if type(image_urls) is list:
        urls = image_urls
        urls = sort_by_site_generic_order(urls, brand)
    else:
        urls = [image_urls]
    urls = [parse_url(url) for url in urls]
    return urls

def create_or_update_images(product, image_urls, brand, image_directory):
    current_images = ProductImage.objects.filter(product_id=product.pk)
    if current_images.count() != len(image_urls):
        logger.info('Updating images of %s, from %s images to %s images', 
            product.pk,
            current_images.count(),
            len(image_urls)
            )
        current_images.delete()
        urls = format_image_urls(image_urls, brand)
        save_for_similarity(image_directory, urls[0])
        for product_image_url in urls:
            create_product_image(product, image_directory, product_image_url)

def create_or_update_size_variants(product, sizes):
    sizes = list(set(sizes)) # Delete duplicates
    size_variant = product.product_type.variant_attributes.get(slug='size')
    size_variants = ProductVariant.objects.filter(
                                            product_id=product.pk, 
                                            attributes__has_key=str(size_variant.pk)
                                            )
    if size_variants.count() != len(sizes):
        logger.info('Updating sizes of product_id %s, from %s sizes to %s sizes', 
            product.pk,
            size_variants.count(),
            len(sizes),
            )
        size_variants.delete()
        for size in sizes:
            create_size_variant(product, size, size_variant)

def create_size_variant(product, size, size_variant):
    defaults = {
        'product': product,
        'quantity': 1,
        'cost_price': 1,
        'quantity_allocated': 0}
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
    image = generate_image(placeholder_dir, url)
    product_image = ProductImage(product=product, image=image)
    product_image.save()
    create_product_thumbnails.delay(product_image.pk)
    return product_image

def add_file_extention(name, content_type):
    extension = mimetypes.guess_extension(content_type)
    if extension in VALID_IMAGE_EXTENSIONS:
        return name + extension
    else:
        logger.error('Unknown/Invalid extension %s from content type %s', 
            extension,
            content_type)

# TODO: refactor this!
def generate_image(image_dir, url, local=False):
    request = req.Request(url, headers=HEADERS)
    image_name = str(hash(url))
    try:
        response = req.urlopen(request, timeout=10)
        content_type = response.headers.get_content_type()
        image_name = add_file_extention(image_name, content_type)
        if image_name is None:
            return NA_IMAGE_PATH
        file_path = os.path.join(image_dir, image_name)
        image = response.read()
        if not local:
            STORAGE_CLIENT.put_object(Key=file_path, Body=image,
                        Bucket=STORAGE_BUCKET)
        else:
            f = open(file_path, 'wb')
            f.write(image)
            f.close()
    except timeout:
        logger.error('socket timed out - %s', url, exc_info=True)
        return NA_IMAGE_PATH
    except:
        logger.error('Error generating image - %s', url, exc_info=True)
        return NA_IMAGE_PATH
    return file_path

def _exists_in_s3(client, bucket, key):
    """return the key's size if it exist, else None"""
    try:
        obj = client.head_object(Bucket=bucket, Key=key)
        return obj['ContentLength']
    except ClientError as exc:
        if exc.response['Error']['Code'] != '404':
            raise

def sort_by_site_generic_order(urls, brand):
    if brand in BRAND_REORDER:
        order = BRAND_REORDER[brand]
        result = []
        for i in range(min(len(urls),len(order))):
            result.append(urls[order[i]])
        return result
    else:
        return urls


def save_for_similarity(image_directory, url):
    similarity_directory = os.path.join(image_directory, 'similarity')
    if not os.path.exists(similarity_directory):
        os.makedirs(similarity_directory)
    image = generate_image(similarity_directory, url, local=False)