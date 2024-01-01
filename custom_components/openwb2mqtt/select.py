"""OpenWB Selector"""
from __future__ import annotations

import copy
import logging

from homeassistant.components import mqtt
from homeassistant.components.select import DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import OpenWBBaseEntity
from .const import (
    MANUFACTURER,
    # CHARGE_POINTS,
    MQTT_ROOT_TOPIC,
    SELECTS_GLOBAL,
    SELECTS_PER_CHARGEPOINT,
    SELECTS_PER_LP,
    openwbSelectEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    integrationUniqueID = config_entry.unique_id
    mqttRoot = config_entry.data[MQTT_ROOT_TOPIC]
    devicetype = config_entry.data["DEVICETYPE"]
    deviceID = config_entry.data["DEVICEID"]
    # nChargePoints = config_entry.data[CHARGE_POINTS]

    selectList = []

    if devicetype == "chargepoint":
        SELECTS_PER_CHARGEPOINT_CP = copy.deepcopy(SELECTS_PER_CHARGEPOINT)
        for description in SELECTS_PER_CHARGEPOINT_CP:
            # description.mqttTopicCommand = None
            description.mqttTopicCurrentValue = None
            selectList.append(
                openwbSelect(
                    unique_id=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=f"Chargepoint {deviceID}",
                    deviceID=deviceID,
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
        deviceID: int | None = None,
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

        self._attr_current_option = None
        self.deviceID = deviceID
        self.mqtt_root = mqtt_root

    # async def async_added_to_hass(self):
    #     """Subscribe to MQTT events."""

    #     @callback
    #     def message_received(message):
    #         """Handle new MQTT messages."""
    #         try:
    #             self._attr_current_option = (
    #                 self.entity_description.valueMapCurrentValue.get(
    #                     int(message.payload)
    #                 )
    #             )
    #         except ValueError:
    #             self._attr_current_option = None

    #         self.async_write_ha_state()

    #     # Subscribe to MQTT topic and connect callack message
    #     if self.entity_description.mqttTopicCurrentValue is not None:
    #         await mqtt.async_subscribe(
    #             self.hass,
    #             self.entity_description.mqttTopicCurrentValue,
    #             message_received,
    #             1,
    #         )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        success = self.publishToMQTT(option)
        if success:
            self._attr_current_option = option
            self.async_write_ha_state()
        else:
            _LOGGER.error("Error publishing MQTT message")

    def publishToMQTT(self, commandValueToPublish) -> bool:
        # topic = f"{self.entity_description.mqttTopicCommand}"
        publish_mqtt_message = False
        chargeTemplateID = self.get_assigned_charge_profile(
            self.hass,
            "openwb2mqtt",
        )
        if chargeTemplateID is not None:
            topic = f"{self.mqtt_root}/{self.entity_description.mqttTopicCommand}/{chargeTemplateID}/chargemode/selected"
            _LOGGER.debug("MQTT topic: %s", topic)
            try:
                payload = self.entity_description.valueMapCommand.get(
                    commandValueToPublish
                )
                _LOGGER.debug("MQTT payload: %s", payload)
                publish_mqtt_message = True
            except ValueError:
                publish_mqtt_message = False

            if publish_mqtt_message:
                self.hass.components.mqtt.publish(self.hass, topic, payload)

        return publish_mqtt_message

    @callback
    def get_assigned_charge_profile(
        self, hass: HomeAssistant, domain: str
    ) -> str | None:
        """Get the chosen pipeline for a domain."""
        ent_reg = entity_registry.async_get(hass)
        # sensor.openwb_openwb_chargepoint_4_lade_profil
        unique_id = slugify(f"{self.mqtt_root}_chargepoint_{self.deviceID}_lade_profil")
        charge_profile_id = ent_reg.async_get_entity_id(
            Platform.SENSOR,
            "openwb2mqtt",
            unique_id,
        )
        if charge_profile_id is None:
            return None

        state = hass.states.get(charge_profile_id)
        if state is None:
            return None

        return state.state
