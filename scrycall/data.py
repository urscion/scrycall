import time
import requests
import requests.utils
import traceback

from .cache import UrlCardCache, CardCache


URL_CACHE = UrlCardCache()
CARD_CACHE = CardCache()
CAN_WRITE_CACHE = True
CAN_READ_CACHE = True
USE_API = True


def get_cards_from_query(query: str) -> list[dict]:
    """Get a list of cards from a query string

    Args:
        query: query string

    Returns:
        List of cards
    """
    url = f"https://api.scryfall.com/cards/search?q={requests.utils.requote_uri(query)}"
    return load_cards(url)


# TODO: this makes some assumptions about the shape of the data
# TODO: make this less clunky
def get_uri_attribute(url):
    """Call a URI nested in card data

    Args:
        url: url

    Returns:
        json data
    """
    json_data = URL_CACHE.load_item(url) if CAN_READ_CACHE else None
    if json_data is None:
        if USE_API:
            json_data = get_api_data_from_url(url)
            if json_data and CAN_WRITE_CACHE:
                URL_CACHE.store_url(url, [json_data])
    elif CAN_READ_CACHE:
        json_data = CARD_CACHE.load_item(json_data[0])
    return json_data


def load_cards(url) -> list[dict]:
    """Load cards.

    Uses module-level parameters to set behaviour.
    CAN_READ_CACHE - Read from the cache
    CAN_WRITE_CACHE - Write to the cache
    USE_API - Use the Scryfall API

    Args:
        url: URL to load from
    """
    # the query url is tied to a list of card ids
    # each card id is tied to cached json data for the card itself
    cards = []
    if CAN_READ_CACHE:
        try:
            card_uids = URL_CACHE.load_item(URL_CACHE.__class__.uid(url)) or []
            for card_uid in card_uids:
                card = CARD_CACHE.load_item(card_uid)
                if not card and USE_API:
                    card_uuid = card_uid.split("_")[-1]
                    card = get_api_data_from_url(
                        f"https://api.scryfall.com/cards/{card_uuid}"
                    )
                    if card and CAN_WRITE_CACHE:
                        CARD_CACHE.store_card(card)
                cards.append(card)
        except Exception:
            traceback.print_exc()
            pass
    if not cards and USE_API:
        json_data = get_api_data_from_url(url)
        if json_data:
            cards = get_cards_from_json_data(json_data)
            if CAN_WRITE_CACHE:
                URL_CACHE.store_url(url, cards)
                for card in cards:
                    CARD_CACHE.store_card(card)
    return cards


def get_cards_from_json_data(data):
    """Get a list of cards from the api json data.

    Args:
        data: Card JSON data from Scryfall

    Returns:
        List of card
    """
    cards = data["data"]
    if data["has_more"]:
        next_url = data["next_page"]
        cards += load_cards(next_url)
    return cards


def get_api_data_from_url(url) -> dict:
    """Call the api and return the data

    100ms delay between calls per https://scryfall.com/docs/api
    """
    time.sleep(0.1)
    resp = requests.get(url)
    if not resp.ok:
        print(resp.text)
        return {}
    return resp.json()
