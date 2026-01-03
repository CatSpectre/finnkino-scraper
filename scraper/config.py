import os

# Base hosts
BASE_URL = os.getenv("FINNKINO_BASE_URL", "https://www.finnkino.fi")
OMNIA_API_HOST = os.getenv("FINNKINO_API_OMNIA_HOST", BASE_URL + "/api/omnia/v1")
DIGITAL_API_HOST = os.getenv("FINNKINO_DIGITAL_API_HOST", "https://digital-api.finnkino.fi/WSVistaWebClient/ocapi/v1")

# Endpoints
THEATERS_LIST = (
    OMNIA_API_HOST +
    "/pageList?friendly=/teatterit/&properties=name&properties=urlSegment&properties=url&properties=nodeId&properties=alias&properties=createDate&properties=updateDate&properties=versions&properties=addressLine1&properties=addressLine2&properties=addressLine3&properties=postCode&properties=longitude&properties=latitude&properties=sitePickerCinemaAttributes&properties=vistaCinema&properties=foodAndBeverageEnabled&properties=filmAndExperienceShowtimePickerCinemaSubtitle&properties=cinemaMapURL"
)
CAMPAIGNS_LIST = (
    OMNIA_API_HOST +
    "/pageList?friendly=/edut-ja-kampanjat/&properties=nodeId&properties=promoTileTitle&properties=promoTileMessage&properties=urlSegment&properties=relatedFilms&properties=type"
)
CINEMA_FEATURE = (
    OMNIA_API_HOST +
    "/extensions/cinemaFeature"
)

GIFT_SHOP_ITEMS = ( 
    DIGITAL_API_HOST +
    "/gift-shop/item-profile"
)
GIFT_SHOP_ITEM_AVAILABILITY = (
    DIGITAL_API_HOST +
    "/gift-shop/item-availability"
)
THEATER_SHOWTIMES = (
    DIGITAL_API_HOST + 
    "/showtimes/by-business-date/{date}?siteIds={site_id}"
)
SEAT_AVAILABILITY = (
    DIGITAL_API_HOST + 
    "/showtimes/{show_id}/seat-availability"
)

# Playwright default
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/119.0.0.0 Safari/537.36"
)
