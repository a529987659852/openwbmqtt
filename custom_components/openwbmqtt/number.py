from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from os import device_encoding, stat

from homeassistant.components import mqtt
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (DEVICE_DEFAULT_NAME, ELECTRIC_CURRENT_AMPERE,
                                 ENERGY_KILO_WATT_HOUR, ENTITY_CATEGORY_CONFIG,
                                 PERCENTAGE)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import slugify
from sqlalchemy import desc

from . import DOMAIN
from .common import OpenWBBaseEntity
# Import global values.
from .const import (CHARGE_POINTS, MQTT_ROOT_TOPIC, NUMBERS_PER_LP,
                    openWBNumberEntityDescription)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for openWB."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    nChargePoints = config.data[CHARGE_POINTS]

    numberList = []

    # TODO: Global Numbers

    for chargePoint in range(1, nChargePoints + 1):
        NUMBERS_PER_LP_COPY = copy.deepcopy(NUMBERS_PER_LP)
        for description in NUMBERS_PER_LP_COPY:
            description.mqttTopicCommand = f"{mqttRoot}/config/set/sofort/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = (
                f"{mqttRoot}/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"
            )

            numberList.append(
                openWBNumber(
                    unique_id=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                    state=description.min_value,
                )
            )
    async_add_entities(numberList)


class openWBNumber(OpenWBBaseEntity, NumberEntity):
    """Entity representing openWB numbers"""

    entity_description: openWBNumberEntityDescription

    def __init__(
        self,
        unique_id: str,
        state: float,
        device_friendly_name: str,
        mqtt_root: str,
        description: openWBNumberEntityDescription,
        currentChargePoint: int | None = 1,
        nChargePoints: int | None = 1,
        min_value: float | None = None,
        max_value: float | None = None,
        step: float | None = None,
        mode: NumberMode = NumberMode.AUTO,
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )
        """Initialize the Demo Number entity."""

        self.entity_description = description

        if nChargePoints:
            self._attr_unique_id = slugify(
                f"{unique_id}-CP{currentChargePoint}-{description.name}"
            )
            self.entity_id = (
                f"number.{unique_id}-CP{currentChargePoint}-{description.name}"
            )
            self._attr_name = f"{description.name} (LP{currentChargePoint})"
        else:
            self._attr_unique_id = slugify(f"{unique_id}-{description.name}")
            self.entity_id = f"number.{unique_id}-{description.name}"
            self._attr_name = description.name

        self._attr_value = state
        self._attr_mode = mode

        if min_value is not None:
            self._attr_min_value = min_value
        if max_value is not None:
            self._attr_max_value = max_value
        if step is not None:
            self._attr_step = step

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_value = float(message.payload)
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

    async def async_set_value(self, value):
        """Update the current value."""
        self._attr_value = value
        self.publishToMQTT()
        self.async_write_ha_state()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        payload = str(int(self._attr_value))
        _LOGGER.debug("MQTT payload: %s", payload)
        self.hass.components.mqtt.publish(self.hass, topic, payload)
