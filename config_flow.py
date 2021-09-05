from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.util import slugify

# Import global parameters
from .const import DATA_SCHEMA, DOMAIN, MQTT_ROOT_TOPIC


class openwbmqttConfigFlow(ConfigFlow, domain=DOMAIN):
    """If the integration is added by the user, ask for the configuration data as defined in DATA_SCHEMA"""
    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user", 
                data_schema = DATA_SCHEMA
            )

        title = f"{DOMAIN}-{user_input[MQTT_ROOT_TOPIC]}"
        title = title.replace("/","_")
        title = slugify(title)
        
        # abort if the same integration was already configured
        await self.async_set_unique_id(title)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title= title,
            data=user_input,
        )