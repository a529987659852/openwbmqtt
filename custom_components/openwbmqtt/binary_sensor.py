"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import DOMAIN, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import OpenWBBaseEntity

# Import global values.
from .const import (
    BINARY_SENSORS_PER_LP,
    CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    openwbBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for openWB."""
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    nChargePoints = config.data[CHARGE_POINTS]

    sensorList = []

    # Create all sensors for each charge point, respectively.
    for chargePoint in range(1, nChargePoints + 1):
        local_sensors_per_lp = copy.deepcopy(BINARY_SENSORS_PER_LP)
        for description in local_sensors_per_lp:
            description.mqttTopicCurrentValue = (
                f"{mqttRoot}/lp/{str(chargePoint)}/{description.key}"
            )
            _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
            sensorList.append(
                openwbBinarySensor(
                    uniqueID=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                )
            )

    async_add_entities(sensorList)


class openwbBinarySensor(OpenWBBaseEntity, BinarySensorEntity):
    """Representation of an openWB sensor that is updated via MQTT."""

    entity_description: openwbBinarySensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: openwbBinarySensorEntityDescription,
        nChargePoints: int | None = None,
        currentChargePoint: int | None = None,
    ) -> None:
        """Initialize the sensor."""

        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )

        self.entity_description = description
        if nChargePoints:
            self._attr_unique_id = slugify(
                f"{uniqueID}-CP{currentChargePoint}-{description.name}"
            )
            self.entity_id = (
                f"{DOMAIN}.{uniqueID}-CP{currentChargePoint}-{description.name}"
            )
            self._attr_name = f"{description.name} (LP{currentChargePoint})"
        else:
            self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
            self.entity_id = f"{DOMAIN}.{uniqueID}-{description.name}"
            self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_is_on = bool(int(message.payload))

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
