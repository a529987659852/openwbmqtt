"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

from homeassistant.config_entries import ConfigFlow

# Import global values.
from .const import DATA_SCHEMA, DOMAIN, MQTT_ROOT_TOPIC


class openwbmqttConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configuration flow for the configuration of the openWB integration. When added by the user, he/she
    must provide configuration values as defined in DATA_SCHEMA."""

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        title = f"{user_input[MQTT_ROOT_TOPIC]}"
        # Abort if the same integration was already configured.
        await self.async_set_unique_id(title)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=title,
            data=user_input,
        )