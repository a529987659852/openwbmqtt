"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT."""
from __future__ import annotations

from homeassistant.config_entries import ConfigFlow

# Import global values.
from .const import DATA_SCHEMA, DOMAIN, MQTT_ROOT_TOPIC

devicetype = "DEVICETYPE"
deviceid = "DEVICEID"

from homeassistant import data_entry_flow
from homeassistant import config_entries
from typing import Any


class openwbmqttConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configuration flow for the configuration of the openWB integration.

    When custom component is added by the user, they must provide
    - MQTT root topic
    - Device type
    - Device ID
    --> See DATA_SCHEMA.
    """

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Ask user for configuration data."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
        title = f"{self.user_input[MQTT_ROOT_TOPIC]}-{user_input[devicetype]}-{user_input[deviceid]}"
        await self.async_set_unique_id(title)
        # Abort if the same integration was already configured.
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=title,
            data=user_input,
        )
