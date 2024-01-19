"""OpenWB Selector."""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.select import DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import OpenWBBaseEntity
from .const import (
    CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    SELECTS_GLOBAL,
    SELECTS_PER_LP,
    openwbSelectEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Return selectors."""

    integrationUniqueID = config_entry.unique_id
    mqttRoot = config_entry.data[MQTT_ROOT_TOPIC]
    nChargePoints = config_entry.data[CHARGE_POINTS]

    selectList = []
    global_selects = copy.deepcopy(SELECTS_GLOBAL)
    for description in global_selects:
        description.mqttTopicCommand = f"{mqttRoot}/{description.mqttTopicCommand}"
        description.mqttTopicCurrentValue = (
            f"{mqttRoot}/{description.mqttTopicCurrentValue}"
        )
        selectList.append(
            openwbSelect(
                unique_id=integrationUniqueID,
                description=description,
                device_friendly_name=integrationUniqueID,
                mqtt_root=mqttRoot,
            )
        )
    for chargePoint in range(1, nChargePoints + 1):
        local_selects_per_lp = copy.deepcopy(SELECTS_PER_LP)
        for description in local_selects_per_lp:
            description.mqttTopicCommand = f"{mqttRoot}/config/set/sofort/lp/{str(chargePoint)}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqttRoot}/config/get/sofort/lp/{str(chargePoint)}/{description.mqttTopicCurrentValue}"
            selectList.append(
                openwbSelect(
                    unique_id=integrationUniqueID,
                    description=description,
                    nChargePoints=int(nChargePoints),
                    currentChargePoint=chargePoint,
                    device_friendly_name=integrationUniqueID,
                    mqtt_root=mqttRoot,
                )
            )
    async_add_entities(selectList)


class openwbSelect(OpenWBBaseEntity, SelectEntity):
    """Entity representing the inverter operation mode."""

    entity_description: openwbSelectEntityDescription

    def __init__(
        self,
        unique_id: str,
        device_friendly_name: str,
        description: openwbSelectEntityDescription,
        mqtt_root: str,
        currentChargePoint: int | None = None,
        nChargePoints: int | None = None,
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
        )
        # Initialize the inverter operation mode setting entity
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

        self._attr_options = description.modes
        self._attr_current_option = None

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            """Handle new MQTT messages."""
            try:
                self._attr_current_option = (
                    self.entity_description.valueMapCurrentValue.get(
                        int(message.payload)
                    )
                )
            except ValueError:
                self._attr_current_option = None

            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        if self.entity_description.mqttTopicCurrentValue is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                message_received,
                1,
            )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option.

        After select --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self.publishToMQTT(option)
        # self._attr_current_option = option
        # self.async_write_ha_state()

    def publishToMQTT(self, commandValueToPublish):
        """Publish data to MQTT."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        _LOGGER.debug("MQTT topic: %s", topic)
        try:
            payload = self.entity_description.valueMapCommand.get(commandValueToPublish)
            _LOGGER.debug("MQTT payload: %s", payload)
            publish_mqtt_message = True
        except ValueError:
            publish_mqtt_message = False

        if publish_mqtt_message:
            self.hass.components.mqtt.publish(self.hass, topic, payload)
