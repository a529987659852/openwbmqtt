"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT."""
from __future__ import annotations

import copy
import logging

# from sqlalchemy import desc
from homeassistant.components import mqtt
from homeassistant.components.number import DOMAIN, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import OpenWBBaseEntity

# Import global values.
from .const import (
    CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    NUMBERS_GLOBAL,
    NUMBERS_PER_LP,
    openWBNumberEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for openWB."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    nChargePoints = config.data[CHARGE_POINTS]

    numberList = []

    NUMBERS_GLOBAL_COPY = copy.deepcopy(NUMBERS_GLOBAL)
    for description in NUMBERS_GLOBAL_COPY:
        if description.mqttTopicCommand.startswith("/"):
            description.mqttTopicCommand = f"{mqttRoot}{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqttRoot}{description.mqttTopicCurrentValue}"
        else:
            description.mqttTopicCommand = f"{mqttRoot}/config/set/{str(description.mqttTopicChargeMode)}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqttRoot}/config/get/{str(description.mqttTopicChargeMode)}/{description.mqttTopicCurrentValue}"

        numberList.append(
            openWBNumber(
                unique_id=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
                # state=description.min_value,
            )
        )

    for chargePoint in range(1, nChargePoints + 1):
        NUMBERS_PER_LP_COPY = copy.deepcopy(NUMBERS_PER_LP)
        for description in NUMBERS_PER_LP_COPY:
            if description.mqttTopicChargeMode:
                description.mqttTopicCommand = f"{mqttRoot}/config/set/{str(description.mqttTopicChargeMode)}/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqttRoot}/config/get/{str(description.mqttTopicChargeMode)}/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"
            else:  # for manual SoC module
                description.mqttTopicCommand = f"{mqttRoot}/set/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqttRoot}/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"

            numberList.append(
                openWBNumber(
                    unique_id=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                    # state=description.min_value,
                )
            )
    async_add_entities(numberList)


class openWBNumber(OpenWBBaseEntity, NumberEntity):
    """Entity representing openWB numbers."""

    entity_description: openWBNumberEntityDescription

    def __init__(
        self,
        unique_id: str,
        device_friendly_name: str,
        mqtt_root: str,
        description: openWBNumberEntityDescription,
        state: float | None = None,
        currentChargePoint: int | None = None,
        nChargePoints: int | None = None,
        native_min_value: float | None = None,
        native_max_value: float | None = None,
        native_step: float | None = None,
        mode: NumberMode = NumberMode.AUTO,
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description

        if nChargePoints:
            self._attr_unique_id = slugify(
                f"{unique_id}-CP{currentChargePoint}-{description.name}"
            )
            self.entity_id = (
                f"{DOMAIN}.{unique_id}-CP{currentChargePoint}-{description.name}"
            )
            self._attr_name = f"{description.name} (LP{currentChargePoint})"
        else:
            self._attr_unique_id = slugify(f"{unique_id}-{description.name}")
            self.entity_id = f"{DOMAIN}.{unique_id}-{description.name}"
            self._attr_name = description.name

        # if state is not None:
        #     self._attr_value = state
        # else:
        self._attr_native_value = state

        self._attr_mode = mode

        if native_min_value is not None:
            self._attr_native_min_value = native_min_value
        if native_max_value is not None:
            self._attr_native_max_value = native_max_value
        if native_step is not None:
            self._attr_native_step = native_step

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_native_value = float(message.payload)
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

    async def async_set_native_value(self, value):
        """Update the current value.

        After set_value --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self._attr_native_value = value
        self.publishToMQTT()
        # self.async_write_ha_state()

    def publishToMQTT(self):
        """Publish data to MQTT."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        payload = str(int(self._attr_native_value))
        _LOGGER.debug("MQTT payload: %s", payload)
        self.hass.components.mqtt.publish(self.hass, topic, payload)
