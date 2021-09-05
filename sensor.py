"""Support for openWB sensors through MQTT."""
from __future__ import annotations

import copy
import logging

import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import callback
from homeassistant.util import slugify

# Import global parameters
from .const import (CHARGE_POINTS, DOMAIN, MQTT_ROOT_TOPIC, SENSORS_GLOBAL,
                    SENSORS_PER_LP, openwbSensorEntityDescription)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, async_add_entities):

    """Reuse data obtained in the configuration flow so that it can be used when setting up the entries.
    Data flow is config_flow.py --> data --> init.py --> hass.data --> sensor.py --> hass.data """
    CONFIG_DATA = hass.data[DOMAIN]

    """Set up sensors for openWB."""
    sensorList = []
    # Global sensors
    for description in SENSORS_GLOBAL:
        description.key = CONFIG_DATA[MQTT_ROOT_TOPIC] + '/' + description.key
        _LOGGER.debug("MQTT topic: %s", description.key)
        sensorList.append(openwbSensor(description=description))
    
    # Sensors applying to each charge point
    for chargePoint in range(1, int(CONFIG_DATA[CHARGE_POINTS]) + 1):
        local_sensors_per_lp = copy.deepcopy(SENSORS_PER_LP)
        for description in local_sensors_per_lp:
            description.key = CONFIG_DATA[MQTT_ROOT_TOPIC] + '/lp/' + str(chargePoint) + '/' + description.key
            _LOGGER.debug("MQTT topic: %s", description.key)
            sensorList.append(openwbSensor(description=description))
    
    async_add_entities(sensorList)

class openwbSensor(SensorEntity):
    """Representation of an openWB that is updated via MQTT."""

    entity_description: openwbSensorEntityDescription

    def __init__(self, description: openwbSensorEntityDescription) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        slug = slugify(description.key.replace("/", "_"))
        self._attr_name = description.key
        self._attr_unique_id = slug

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            if self.entity_description.state is not None:
                self._attr_native_value = self.entity_description.state(message.payload)
            else:
                self._attr_native_value = message.payload

            #Map values as defined in the value map dict
            if self.entity_description.valueMap is not None:
                try:
                    self._attr_native_value = self.entity_description.valueMap.get(int(self._attr_native_value))
                except ValueError:
                    self._attr_native_value = self._attr_native_value
            
            #Reformat TimeRemaining --> hh:mm
            if 'TimeRemaining' in self.entity_description.key:
                if 'H' in self._attr_native_value:
                    tmp = self._attr_native_value.split() 
                    self._attr_native_value = f"{int(tmp[0]):02d}:{int(tmp[2]):02d}"
                elif 'Min' in self._attr_native_value:
                    tmp = self._attr_native_value.split() 
                    self._attr_native_value = f"00:{int(tmp[0]):02d}"
            
            #Update entity state with value published on MQTT
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass, self.entity_description.key, message_received, 1
        )
