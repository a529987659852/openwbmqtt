"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CHARGE_POINTS, DOMAIN, MQTT_ROOT_TOPIC

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    # Provide data obtained in the configuration flow so that it can be used when setting up the entries 
    hass.data.setdefault(DOMAIN, {MQTT_ROOT_TOPIC: {}})
    hass.data[DOMAIN][MQTT_ROOT_TOPIC] = entry.data[MQTT_ROOT_TOPIC]
    hass.data.setdefault(DOMAIN, {CHARGE_POINTS: {}})
    hass.data[DOMAIN][CHARGE_POINTS] = entry.data[CHARGE_POINTS]

    # Trigger the creation of sensors
    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
        
    """Define services that publish data to MQTT. The published data is subscribed by openWB
    and the respective settings are changed."""

    #Prefix: If the openWB mqtt server is briged to a central mqtt server, a prefix is required.
    mqttprefix = entry.data[MQTT_ROOT_TOPIC]
    _LOGGER.debug("mqttprefix: %s", mqttprefix)
    
    #Define functions to execute on service call
    def fun_enable_disable_cp(call):
        """Enable or disable charge point # --> set/lp#/ChargePointEnabled [0,1]"""
        topic = f"{mqttprefix}/set/lp{call.data.get('charge_point_id')}/ChargePointEnabled"
        _LOGGER.debug("topic (enable_disable_cp): %s", topic)

        if call.data.get('selected_status') =='On':
            hass.components.mqtt.publish(topic, '1')
        else:
            hass.components.mqtt.publish(topic, '0')

    def fun_change_global_charge_mode(call):
        """Change the wallbox global charge mode --> set/ChargeMode [0, .., 3]"""
        topic = f"{mqttprefix}/set/ChargeMode"
        _LOGGER.debug("topic (change_global_charge_mode): %s", topic)

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
        """If box is in state 'Sofortladen', the charge limitation can be finetuned.
        --> config/set/sofort/lp/#/chargeLimitation [0, 1, 2].
        If the wallbox shall charge only a limited amount of energy [1] or to a certain SOC [2]
        --> config/set/sofort/lp/#/energyToCharge [value in kWh]
        --> config/set/sofort/lp/#/socToChargeTo [value in %]
        """
        topic = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/chargeLimitation"
        _LOGGER.debug("topic (change_charge_limitation_per_cp): %s", topic)
        
        if call.data.get('charge_limitation') == "Not limited":
            payload = str(0)
            hass.components.mqtt.publish(topic, payload)
        elif call.data.get('charge_limitation') == "kWh":
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
        """Set the charge current per loading point --> config/set/sofort/lp/#/current [value in A]"""
        topic = f"{mqttprefix}/config/set/sofort/lp/{call.data.get('charge_point_id')}/current"
        _LOGGER.debug("topic (fun_change_charge_current_per_cp): %s", topic)
        
        payload = str(call.data.get('target_current'))
        hass.components.mqtt.publish(topic, payload)

    # Register our services with Home Assistant.
    hass.services.async_register(DOMAIN, 'enable_disable_cp', fun_enable_disable_cp)
    hass.services.async_register(DOMAIN, 'change_global_charge_mode', fun_change_global_charge_mode)
    hass.services.async_register(DOMAIN, 'change_charge_limitation_per_cp', fun_change_charge_limitation_per_cp)
    hass.services.async_register(DOMAIN, 'change_charge_current_per_cp', fun_change_charge_current_per_cp)
    
    # Return boolean to indicate that initialization was successfully.
    return True