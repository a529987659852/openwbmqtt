"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

import copy
from datetime import timedelta
import logging

from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    CONF_HOST,
)
from homeassistant.components import mqtt
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt, slugify

from homeassistant.helpers.entity import DeviceInfo

# Import global values.
from .const import (
    CHARGE_POINTS,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    MQTT_ROOT_TOPIC,
    SENSORS_GLOBAL,
    BINARY_SENSORS_PER_LP,
    openwbBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for openWB."""

    """Reuse data obtained in the configuration flow so that it can be used when setting up the entries.
    Data flow is config_flow.py --> data --> init.py --> hass.data --> sensor.py --> hass.data"""
    # nChargePoints = hass.data[DOMAIN][config.entry_id][CHARGE_POINTS]
    # mqttRoot = hass.data[DOMAIN][config.entry_id][MQTT_ROOT_TOPIC]
    # confHost = hass.data[DOMAIN][config.entry_id][CONF_HOST]
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    nChargePoints = config.data[CHARGE_POINTS]
    confHost = config.data[CONF_HOST]

    sensorList = []
    # # Create all global sensors.
    # global_sensors = copy.deepcopy(SENSORS_GLOBAL)
    # for description in global_sensors:
    #     description.mqttTopic = f"{mqttRoot}/{description.key}"
    #     _LOGGER.debug("mqttTopic: %s", description.mqttTopic)
    #     sensorList.append(
    #         openwbSensor(uniqueID=integrationUniqueID, description=description, confHost=confHost)
    #     )

    # Create all sensors for each charge point, respectively.
    for chargePoint in range(1, nChargePoints + 1):
        local_sensors_per_lp = copy.deepcopy(BINARY_SENSORS_PER_LP)
        for description in local_sensors_per_lp:
            description.mqttTopic = (
                f"{mqttRoot}/lp/{str(chargePoint)}/{description.key}"
            )
            _LOGGER.debug("mqttTopic: %s", description.mqttTopic)
            sensorList.append(
                openwbBinarySensor(
                    uniqueID=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    confHost=confHost,
                )
            )

    async_add_entities(sensorList)


class openwbBinarySensor(BinarySensorEntity):
    """Representation of an openWB sensor that is updated via MQTT."""

    entity_description: openwbBinarySensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        confHost: str | None,
        description: openwbBinarySensorEntityDescription,
        nChargePoints: int | None = None,
        currentChargePoint: int | None = None,
    ) -> None:
        """Initialize the sensor."""
        # Group all sensors to one device. The device is identified by the prefix (which is unique).
        self._attr_device_info = DeviceInfo(
            name= uniqueID,
            identifiers= {(DOMAIN, uniqueID)},
            manufacturer= MANUFACTURER,
            model= MODEL,
            configuration_url=f"http://{confHost}/openWB/web/index.php",
        )
        self.entity_description = description
        if nChargePoints:
            self._attr_unique_id = slugify(
                f"{uniqueID}-CP{currentChargePoint}-{description.name}"
            )
            self.entity_id = f"binary_sensor.{uniqueID}-CP{currentChargePoint}-{description.name}"
            self._attr_name = f"{description.name} (LP{currentChargePoint})"
        else:
            self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
            self.entity_id = f"binary_sensor.{uniqueID}-{description.name}"
            self._attr_name = description.name

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            #if self.entity_description.state is not None:
            #     self._attr_is_on = bool(self.entity_description.state(int(message.payload)))
            # else:
            self._attr_is_on = bool(int(message.payload))

            # Update entity state with value published on MQTT.
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass, self.entity_description.mqttTopic, message_received, 1
        )
