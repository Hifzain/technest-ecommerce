from django.core.cache import cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product


def _build_corpus():
    """Builds a text fingerprint for every active product using its name, description, category, brand, and specs."""
    products = list(
        Product.objects.filter(status=1).select_related('category', 'brand').prefetch_related('specifications')
    )
    corpus = []
    for p in products:
        specs_text = ' '.join(f"{s.key} {s.value}" for s in p.specifications.all())
        brand_name = p.brand.name if p.brand else ''
        text = f"{p.name} {p.short_description} {p.category.name} {brand_name} {specs_text}"
        corpus.append(text)
    return products, corpus


def get_similar_products(product, top_n=4):
    """
    Content-based recommendations using TF-IDF + cosine similarity.
    Pure local ML, no external API calls. Cached for 6 hours.
    """
    cache_key = f"similar_products_{product.pk}"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return Product.objects.filter(pk__in=cached_ids, status=1)

    products, corpus = _build_corpus()
    if len(products) < 2:
        return Product.objects.none()

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)

    try:
        idx = next(i for i, p in enumerate(products) if p.pk == product.pk)
    except StopIteration:
        return Product.objects.none()

    sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    ranked_indices = sim_scores.argsort()[::-1]

    result_ids = []
    for i in ranked_indices:
        if products[i].pk != product.pk:
            result_ids.append(products[i].pk)
        if len(result_ids) >= top_n:
            break

    cache.set(cache_key, result_ids, 60 * 60 * 6)
    return Product.objects.filter(pk__in=result_ids)


def invalidate_similarity_cache(product_id=None):
    """Call this after editing/creating products so recommendations stay fresh."""
    if product_id:
        cache.delete(f"similar_products_{product_id}")
