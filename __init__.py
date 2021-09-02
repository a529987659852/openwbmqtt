# """
# Example of a custom MQTT component.

# Shows how to communicate with MQTT. Follows a topic on MQTT and updates the
# state of an entity to the last message received on that topic.

# Also offers a service 'set_state' that will publish a message on the topic that
# will be passed via MQTT to our message received listener. Call the service with
# example payload {"new_state": "some new state"}.

# Configuration:

# To use the mqtt_example component you will need to add the following to your
# configuration.yaml file.

# mqtt_basic:
#   topic: "home-assistant/mqtt_example"
# """
from homeassistant.components import mqtt

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

import logging

_LOGGER = logging.getLogger(__name__)


# The domain of your component. Should be equal to the name of your component.
DOMAIN = "openwbmqtt"

MQTT_ROOT_TOPIC = 'mqttroot'
MQTT_ROOT_TOPIC_DEFAULT = 'openWB'
# CHARGE_POINTS = 'chargepoints'
# DEFAULT_CHARGE_POINTS = [1]
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(MQTT_ROOT_TOPIC,default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):

    mqttprefix = config[DOMAIN][MQTT_ROOT_TOPIC]
    _LOGGER.debug("mqttprefix: %s", mqttprefix)
    
    """Define functions to select on service call"""
    def fun_enable_disable_cp(call):
        topic = f"{mqttprefix}/set/lp{call.data.get('charge_point_id')}/ChargePointEnabled"
        _LOGGER.debug("topic (enable_disable_cp): %s", topic)

        """Service to send a message."""
        if call.data.get('selected_status') =='On':
            hass.components.mqtt.publish(topic, '1')
        else:
            hass.components.mqtt.publish(topic, '0')

    def fun_change_global_charge_mode(call):
        topic = f"{mqttprefix}/set/ChargeMode"
        _LOGGER.debug("topic (change_global_charge_mode): %s", topic)

        """Service to send a message."""
        if call.data.get('global_charge_mode') == "Sofortladen":
            payload = str(0)
        elif  call.data.get('global_charge_mode') == "Min+PV-Laden":
            payload = str(1)
        elif  call.data.get('global_charge_mode') == "Nur PV-Laden": 
            payload = str(2)
        elif  call.data.get('global_charge_mode') == "Stop": 
            payload = str(3)
        else:
            payload = str(4)

        hass.components.mqtt.publish(topic, payload)
    
    def fun_change_charge_limitation_per_cp(call):
        topic = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/chargeLimitation"
        _LOGGER.debug("topic (change_charge_limitation_per_cp): %s", topic)
        if call.data.get('charge_limitation') == "Not limited":
            payload = str(0)
            hass.components.mqtt.publish(topic, payload)
        elif call.data.get('charge_Limitation') == "kWh":
            payload = str(1)
            topic2 = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/energyToCharge"
            payload2 = str(call.data.get('energy_to_charge'))
            hass.components.mqtt.publish(topic, payload)
            hass.components.mqtt.publish(topic2, payload2)
        elif call.data.get('charge_limitation') == "SOC": 
            payload = str(2)
            topic2 = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/socToChargeTo"
            payload2 = str(call.data.get('required_soc'))
            hass.components.mqtt.publish(topic, payload)
            hass.components.mqtt.publish(topic2, payload2)

    def fun_change_charge_current_per_cp(call):
        topic = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/current"
        _LOGGER.debug("topic (fun_change_charge_current_per_cp): %s", topic)
        payload = str(call.data.get('target_current'))
        hass.components.mqtt.publish(topic, payload)

    # Register our service with Home Assistant.
    hass.services.register(DOMAIN, 'enable_disable_cp', fun_enable_disable_cp)
    hass.services.register(DOMAIN, 'change_global_charge_mode', fun_change_global_charge_mode)
    hass.services.register(DOMAIN, 'change_charge_limitation_per_cp', fun_change_charge_limitation_per_cp)
    hass.services.register(DOMAIN, 'change_charge_current_per_cp', fun_change_charge_current_per_cp)

    # Return boolean to indicate that initialization was successfully.
    return True

# Mögliche Settings
#DONE openWB/set/lp1/ChargePointEnabled 0 (LP ausschalten) / 1 (LP einschalten)
#DONE openWB/set/ChargeMode 0 (Sofortladen), 1 (Min+PV Laden), 2 (PV-Laden), 3 (Stop), 4 (Standby)

# Im Modus Sofortladen: Wie soll die Lademenge begrenzt werden?
# openWB/set/lp/1/DirectChargeSubMode 0 (garnicht), 1 (Energiemenge / gel. kWh), 2 (% SoC)
# bei 0:
    # openWB/set/lp/1/DirectChargeSubMode = 0
    # openWB/set/lp/1/DirectChargeSubMode = 0
# bei 1:
    # openWB/set/lp/1/DirectChargeSubMode = 1
    # openWB/set/lp/1/DirectChargeSubMode = 0
# bei 2:
    # openWB/set/lp/1/DirectChargeSubMode = 0
    # openWB/set/lp/1/DirectChargeSubMode = 1
# !! Änderungen werden erst nach nächstem Scriptlauf (ca. 10 sek) auf MQTT publiziert
# !! Änderungen werden nicht im openWB-Web-UI angezeigt
# Wenn man stattdessen hier publiziert:
#openWB/config/set/sofort/lp/1/chargeLimitation (0 = garnicht, 1 = Energiemenge / gel. kWh, 2 %SoC)
# Werden die Änderungen angezeigt. Die Frage ist, ob diese auch konsistent umgeseztt werden??

#openWB/config/set/sofort/lp/1/socToChargeTo --> Maximaler SoC für chargeLimitation  = 2
#openWB/config/set/sofort/lp/1/energyToCharge --> Maximale Energiemenge für chargeLimitation = 1

#openWB/config/set/sofort/lp/1/current --> Sofortladestrom 

# """The dsmr component."""
# from asyncio import CancelledError
# from contextlib import suppress

# from homeassistant.config_entries import ConfigEntry
# from homeassistant.core import HomeAssistant


# DATA_TASK = "task"
# PLATFORMS = ["sensor"]
# DOMAIN = "openwbmqtt"


# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up DSMR from a config entry."""
#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][entry.entry_id] = {}

#     hass.config_entries.async_setup_platforms(entry, PLATFORMS)
#     entry.async_on_unload(entry.add_update_listener(async_update_options))

#     return True

# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
#     task = hass.data[DOMAIN][entry.entry_id][DATA_TASK]

#     # Cancel the reconnect task
#     task.cancel()
#     with suppress(CancelledError):
#         await task

#     unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
#     if unload_ok:
#         hass.data[DOMAIN].pop(entry.entry_id)

#     return unload_ok


# async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Update options."""
#     await hass.config_entries.async_reload(entry.entry_id)
