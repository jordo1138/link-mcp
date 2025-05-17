from app.services.link_filter import filter_link_eligible


def test_filter_link_eligible_returns_only_link_items():
    products = [
        {"id": "p1", "metadata": {"link_eligible": "true"}},
        {"id": "p2", "metadata": {"link_eligible": "false"}},
        {"id": "p3", "metadata": {"link_eligible": "true"}},
    ]
    result = filter_link_eligible(products)
    assert result == [products[0], products[2]]
