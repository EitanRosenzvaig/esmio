from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q

from ...product.models import Product


def search(phrase):
    """Return matching products for storefront views.

    Fuzzy storefront search that is resistant to small typing errors made
    by user. Name is matched using trigram similarity, description uses
    standard postgres full text search.

    Args:
        phrase (str): searched phrase

    """
    name_sim = TrigramSimilarity('name', phrase)
    brand_sim = TrigramSimilarity('brand', phrase)
    published = Q(is_published=True)
    ft_in_description = Q(description__search=phrase)
    name_similar = Q(name_sim__gt=0.2)
    brand_similar = Q(brand_sim__gt=0.5)
    return Product.objects.annotate(name_sim=name_sim, brand_sim=brand_sim).filter(
        (ft_in_description | name_similar | brand_similar) & published)
