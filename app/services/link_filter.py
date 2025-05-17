from typing import List, Dict


def filter_link_eligible(products: List[Dict]) -> List[Dict]:
    """Return products marked as Link eligible via metadata."""
    link_products = []
    for product in products:
        metadata = product.get("metadata", {})
        if metadata.get("link_eligible") == "true":
            link_products.append(product)
    return link_products
