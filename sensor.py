"""Support for openWB sensors through MQTT."""
from __future__ import annotations

from homeassistant.core import callback
from homeassistant.util import slugify
from homeassistant.components import mqtt
from homeassistant.components.sensor import (
    SensorEntity,
    PLATFORM_SCHEMA,
)
import voluptuous as vol

# Import global parameters
from .const import (
    MQTT_ROOT_TOPIC,
    MQTT_ROOT_TOPIC_DEFAULT,
    CHARGE_POINTS,
    DEFAULT_CHARGE_POINTS,
    SENSORS_GLOBAL,
    SENSORS_PER_LP,
    openwbSensorEntityDescription,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(
            MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT
        ): mqtt.valid_subscribe_topic,
        vol.Optional(
            CHARGE_POINTS, default=DEFAULT_CHARGE_POINTS
        ): list
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up sensors for openWB."""
    sensorList = []
    # Global sensors
    for description in SENSORS_GLOBAL:
        description.key = config.get(MQTT_ROOT_TOPIC) + '/' + description.key
        sensorList.append(openwbSensor(description=description))
    
    # Sensors applying to each charge point
    for chargePoint in config.get(CHARGE_POINTS):
        for description in SENSORS_PER_LP:
            description.key = config.get(MQTT_ROOT_TOPIC) + '/lp/' + str(chargePoint) + '/' + description.key
            sensorList.append(openwbSensor(description=description))
    
    async_add_entities(sensorList)

class openwbSensor(SensorEntity):
    """Representation of an openWB that is updated via MQTT."""

    entity_description: openwbSensorEntityDescription

    def __init__(self, description: openwbSensorEntityDescription) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        slug = slugify(description.key.replace("/", "_"))
        self.entity_id = f"sensor.{slug}"

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
