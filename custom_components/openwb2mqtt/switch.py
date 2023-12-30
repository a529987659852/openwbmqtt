from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.switch import DOMAIN, SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import OpenWBBaseEntity
from .const import (
    CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    SWITCHES_PER_LP,
    openwbSwitchEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    integrationUniqueID = config_entry.unique_id
    mqttRoot = config_entry.data[MQTT_ROOT_TOPIC]
    nChargePoints = config_entry.data[CHARGE_POINTS]

    switchList = []

    # todo: global switches

    for chargePoint in range(1, nChargePoints + 1):
        localSwitchesPerLP = copy.deepcopy(SWITCHES_PER_LP)
        for description in localSwitchesPerLP:
            if description.mqttTopicChargeMode:
                description.mqttTopicCommand = f"{mqttRoot}/config/set/{str(description.mqttTopicChargeMode)}/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqttRoot}/config/get/{str(description.mqttTopicChargeMode)}/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"
            else:  # for manual SoC module
                description.mqttTopicCommand = f"{mqttRoot}/set/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqttRoot}/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"
            switchList.append(
                openwbSwitch(
                    unique_id=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                )
            )

    async_add_entities(switchList)


class openwbSwitch(OpenWBBaseEntity, SwitchEntity):
    """Entity representing the inverter operation mode."""

    entity_description: openwbSwitchEntityDescription

    def __init__(
        self,
        unique_id: str,
        device_friendly_name: str,
        description: openwbSwitchEntityDescription,
        mqtt_root: str,
        currentChargePoint: int | None = None,
        nChargePoints: int | None = None,
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )
        """Initialize the inverter operation mode setting entity."""
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

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            if int(message.payload) == 1:
                self._attr_is_on = True
            elif int(message.payload) == 0:
                self._attr_is_on = False
            else:
                self._attr_is_on = None

            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

    def turn_on(self, **kwargs):
        """Turn the switch on.
        After turn_on --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self._attr_is_on = True
        self.publishToMQTT()
        # self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off.
        After turn_off --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self._attr_is_on = False
        self.publishToMQTT()
        # self.schedule_update_ha_state()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommand}"
        self.hass.components.mqtt.publish(self.hass, topic, str(int(self._attr_is_on)))
        """if self._attr_is_on == True:
            self.hass.components.mqtt.publish(self.hass, topic, str(1))
        else:
            self.hass.components.mqtt.publish(self.hass, topic, str(0))
        """
