"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
from datetime import timedelta
import logging
import re

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt, slugify

from .common import OpenWBBaseEntity

# Import global values.
from .const import (
    CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    SENSORS_GLOBAL,
    SENSORS_PER_LP,
    openwbSensorEntityDescription,
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
    # Create all global sensors.
    global_sensors = copy.deepcopy(SENSORS_GLOBAL)
    for description in global_sensors:
        description.mqttTopicCurrentValue = f"{mqttRoot}/{description.key}"
        _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
        sensorList.append(
            openwbSensor(
                uniqueID=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )

    # Create all sensors for each charge point, respectively.
    for chargePoint in range(1, nChargePoints + 1):
        local_sensors_per_lp = copy.deepcopy(SENSORS_PER_LP)
        for description in local_sensors_per_lp:
            description.mqttTopicCurrentValue = (
                f"{mqttRoot}/lp/{str(chargePoint)}/{description.key}"
            )
            _LOGGER.debug("mqttTopic: %s", description.mqttTopicCurrentValue)
            sensorList.append(
                openwbSensor(
                    uniqueID=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                )
            )

    async_add_entities(sensorList)


class openwbSensor(OpenWBBaseEntity, SensorEntity):
    """Representation of an openWB sensor that is updated via MQTT."""

    entity_description: openwbSensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: openwbSensorEntityDescription,
        nChargePoints: int | None = None,
        currentChargePoint: int | None = None,
    ) -> None:
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
                f"sensor.{uniqueID}-CP{currentChargePoint}-{description.name}"
            )
            self._attr_name = f"{description.name} (LP{currentChargePoint})"
        else:
            self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
            self.entity_id = f"sensor.{uniqueID}-{description.name}"
            self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            self._attr_native_value = message.payload

            # Convert data if a conversion function is defined
            if self.entity_description.value_fn is not None:
                self._attr_native_value = self.entity_description.value_fn(
                    self._attr_native_value
                )

            # Map values as defined in the value map dict.
            if self.entity_description.valueMap is not None:
                try:
                    self._attr_native_value = self.entity_description.valueMap.get(
                        int(self._attr_native_value)
                    )
                except ValueError:
                    self._attr_native_value = self._attr_native_value

            # Reformat TimeRemaining --> timestamp.
            if "TimeRemaining" in self.entity_description.key:
                now = dt.utcnow()
                if "H" in self._attr_native_value:
                    tmp = self._attr_native_value.split()
                    delta = timedelta(hours=int(tmp[0]), minutes=int(tmp[2]))
                    self._attr_native_value = now + delta
                elif "Min" in self._attr_native_value:
                    tmp = self._attr_native_value.split()
                    delta = timedelta(minutes=int(tmp[0]))
                    self._attr_native_value = now + delta
                else:
                    self._attr_native_value = None

            # Reformat uptime sensor
            if "uptime" in self.entity_id:
                reluptime = re.match(
                    ".*\sup\s(.*),.*\d*user.*", self._attr_native_value
                )[1]
                days = 0
                if re.match("(\d*)\sday.*", reluptime):
                    days = re.match("(\d*)\sday", reluptime)[1]
                    reluptime = re.match(".*,\s(.*)", reluptime)[1]
                if re.match(".*min", reluptime):
                    hours = 0
                    mins = re.match("(\d*)\s*min", reluptime)[1]
                else:
                    hours, mins = re.match("\s?(\d*):0?(\d*)", reluptime).group(1, 2)
                self._attr_native_value = f"{days} d {hours} h {mins} min"

            # If MQTT message contains IP --> set up configuration_url to visit the device
            elif "ip_adresse" in self.entity_id:
                device_registry = async_get_dev_reg(self.hass)
                device = device_registry.async_get_device(
                    self.device_info.get("identifiers")
                )
                device_registry.async_update_device(
                    device.id,
                    configuration_url=f"http://{message.payload}/openWB/web/index.php",
                )
                device_registry.async_update_device
            # If MQTT message contains version --> set sw_version of the device
            elif "version" in self.entity_id:
                device_registry = async_get_dev_reg(self.hass)
                device = device_registry.async_get_device(
                    self.device_info.get("identifiers")
                )
                device_registry.async_update_device(
                    device.id, sw_version=message.payload
                )
                device_registry.async_update_device

            # Update icon of countPhasesInUse
            elif "countPhasesInUse" in self.entity_description.key:
                if int(message.payload) == 0:
                    self._attr_icon = "mdi:numeric-0-circle-outline"
                elif int(message.payload) == 1:
                    self._attr_icon = "mdi:numeric-1-circle-outline"
                elif int(message.payload) == 3:
                    self._attr_icon = "mdi:numeric-3-circle-outline"
                else:
                    self._attr_icon = "mdi:numeric"

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
