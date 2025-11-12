"""CSFD News sensor platform."""
from datetime import timedelta
import logging
import aiohttp
import async_timeout
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CSFD_NEWS_URL,
    SCAN_INTERVAL_MINUTES,
    MAX_NEWS_ITEMS,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=SCAN_INTERVAL_MINUTES)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the CSFD News sensor."""
    async_add_entities([CSFDNewsSensor(hass)], True)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up CSFD News sensor from a config entry."""
    async_add_entities([CSFDNewsSensor(hass, config_entry)], True)


class CSFDNewsSensor(SensorEntity):
    """Representation of a CSFD News sensor."""

    def __init__(self, hass: HomeAssistant, config_entry=None) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = DEFAULT_NAME

        # Use config entry ID for unique_id if available (for config flow)
        if config_entry:
            self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}"
        else:
            # Legacy unique_id for YAML configuration
            self._attr_unique_id = f"{DOMAIN}_sensor"

        self._state = 0
        self._news_items = []

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "news": self._news_items,
            "count": self._state,
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:newspaper-variant-outline"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        _LOGGER.info("Starting CSFD news update from %s", CSFD_NEWS_URL)
        try:
            session = async_get_clientsession(self.hass)

            # Add headers to avoid 403 errors from CSFD
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
                "Referer": "https://www.csfd.cz/",
            }

            async with async_timeout.timeout(30):
                _LOGGER.debug("Fetching CSFD news page...")
                async with session.get(CSFD_NEWS_URL, headers=headers) as response:
                    _LOGGER.info("HTTP response: %d %s", response.status, response.reason)

                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching CSFD news: HTTP %s", response.status
                        )
                        return

                    html = await response.text()
                    _LOGGER.debug("Received HTML: %d characters", len(html))

                    self._news_items = await self._parse_news(html)
                    self._state = len(self._news_items)

                    if self._state > 0:
                        _LOGGER.info("✓ Successfully fetched %s news items", self._state)
                    else:
                        _LOGGER.error("✗ Failed to parse any news items from HTML")

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching CSFD news: %s", err)
        except Exception as err:
            _LOGGER.error("Unexpected error fetching CSFD news: %s", err)
            import traceback
            _LOGGER.debug("Traceback: %s", traceback.format_exc())

    async def _parse_news(self, html: str) -> list:
        """Parse news from HTML with multiple fallback strategies."""
        news_items = []

        try:
            soup = BeautifulSoup(html, "html.parser")
            _LOGGER.debug("Parsing HTML (%d chars)", len(html))

            # Strategy 1: Find articles with standard selectors
            articles = soup.find_all("article", limit=MAX_NEWS_ITEMS * 2)
            _LOGGER.info("Strategy 1: Found %d <article> tags", len(articles))

            # Strategy 2: Try news-specific containers
            if not articles:
                _LOGGER.warning("No <article> tags, trying divs with news classes")
                articles = soup.find_all(
                    "div",
                    class_=lambda x: x and any(
                        kw in str(x).lower() for kw in ["news", "article", "box-content"]
                    ),
                    limit=MAX_NEWS_ITEMS * 2
                )
                _LOGGER.info("Strategy 2: Found %d div containers", len(articles))

            # Strategy 3: Header-based extraction
            if not articles:
                _LOGGER.warning("No containers, trying header-based extraction")
                headers_with_links = []
                for h in soup.find_all(["h2", "h3"]):
                    if h.find("a"):
                        headers_with_links.append(h.parent)
                articles = headers_with_links[:MAX_NEWS_ITEMS * 2]
                _LOGGER.info("Strategy 3: Found %d headers with links", len(articles))

            for article in articles[:MAX_NEWS_ITEMS]:
                try:
                    # Extract title and link with multiple patterns
                    title = None
                    link = None

                    # Try h3, h2, then direct a
                    for header_tag in ["h3", "h2", "h4"]:
                        header = article.find(header_tag)
                        if header:
                            link_elem = header.find("a")
                            if link_elem:
                                title = link_elem.get_text(strip=True)
                                link = link_elem.get("href", "")
                                break

                    # Direct a tag as last resort
                    if not title:
                        link_elem = article.find("a")
                        if link_elem:
                            title = link_elem.get_text(strip=True)
                            link = link_elem.get("href", "")

                    if not title or len(title) < 3 or not link:
                        _LOGGER.debug("Skipping item - invalid title or link")
                        continue

                    # Fix relative links
                    if not link.startswith("http"):
                        link = f"https://www.csfd.cz{link}"

                    # Extract image
                    image = ""
                    img_elem = article.find("img")
                    if img_elem:
                        image = img_elem.get("src", "") or img_elem.get("data-src", "")
                        if image and not image.startswith("http"):
                            if image.startswith("//"):
                                image = f"https:{image}"
                            else:
                                image = f"https://www.csfd.cz{image}"

                    # Extract date
                    date = ""
                    time_elem = article.find("time")
                    if time_elem:
                        date = time_elem.get_text(strip=True) or time_elem.get("datetime", "")
                    if not date:
                        date_elem = article.find(class_=lambda x: x and "date" in str(x).lower())
                        if date_elem:
                            date = date_elem.get_text(strip=True)

                    # Extract description
                    perex = ""
                    perex_elem = article.find("p")
                    if perex_elem:
                        perex = perex_elem.get_text(strip=True)

                    news_items.append({
                        "title": title,
                        "link": link,
                        "image": image,
                        "date": date,
                        "perex": perex,
                    })
                    _LOGGER.debug("Parsed: %s", title[:40])

                except Exception as err:
                    _LOGGER.warning("Error parsing item: %s", err)
                    continue

            _LOGGER.info("Successfully parsed %d news items", len(news_items))

            if not news_items:
                _LOGGER.error("No news parsed! HTML may have changed.")
                _LOGGER.debug("Sample HTML: %s", html[:500])

        except Exception as err:
            _LOGGER.error("Parse error: %s", err)

        return news_items
