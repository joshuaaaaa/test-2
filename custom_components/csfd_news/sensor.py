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
        try:
            session = async_get_clientsession(self.hass)
            async with async_timeout.timeout(30):
                async with session.get(CSFD_NEWS_URL) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error fetching CSFD news: HTTP %s", response.status
                        )
                        return

                    html = await response.text()
                    self._news_items = await self._parse_news(html)
                    self._state = len(self._news_items)
                    _LOGGER.debug("Successfully fetched %s news items", self._state)

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching CSFD news: %s", err)
        except Exception as err:
            _LOGGER.error("Unexpected error fetching CSFD news: %s", err)

    async def _parse_news(self, html: str) -> list:
        """Parse news from HTML."""
        news_items = []

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find all news articles
            articles = soup.find_all("article", class_="article", limit=MAX_NEWS_ITEMS)

            for article in articles[:MAX_NEWS_ITEMS]:
                try:
                    # Extract title and link
                    title_elem = article.find("h3", class_="article-title")
                    if not title_elem:
                        continue

                    link_elem = title_elem.find("a")
                    if not link_elem:
                        continue

                    title = link_elem.get_text(strip=True)
                    link = link_elem.get("href", "")
                    if link and not link.startswith("http"):
                        link = f"https://www.csfd.cz{link}"

                    # Extract image
                    img_elem = article.find("img", class_="article-img")
                    image = img_elem.get("src", "") if img_elem else ""
                    if image and not image.startswith("http"):
                        image = f"https://www.csfd.cz{image}"

                    # Extract date/time
                    time_elem = article.find("time", class_="article-date")
                    date = time_elem.get_text(strip=True) if time_elem else ""

                    # Extract perex (short description)
                    perex_elem = article.find("div", class_="article-perex")
                    perex = perex_elem.get_text(strip=True) if perex_elem else ""

                    news_item = {
                        "title": title,
                        "link": link,
                        "image": image,
                        "date": date,
                        "perex": perex,
                    }

                    news_items.append(news_item)

                except Exception as err:
                    _LOGGER.warning("Error parsing news item: %s", err)
                    continue

        except Exception as err:
            _LOGGER.error("Error parsing CSFD news HTML: %s", err)

        return news_items
