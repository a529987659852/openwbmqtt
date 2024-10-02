"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Import global values.
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Trigger the creation of sensors."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Define services that publish data to MQTT. The published data is subscribed by openWB
    # and the respective settings are changed.

    def fun_enable_disable_cp(call):
        """Enable or disable charge point # --> set/lp#/ChargePointEnabled [0,1]."""
        topic = f"{call.data.get('mqtt_prefix')}/set/lp{call.data.get('charge_point_id')}/ChargePointEnabled"
        _LOGGER.debug("topic (enable_disable_cp): %s", topic)

        if call.data.get("selected_status") == "On":
            payload = str(1)
            hass.components.mqtt.publish(hass, topic, payload)

        else:
            payload = str(0)
            hass.components.mqtt.publish(hass, topic, payload)

    def fun_change_global_charge_mode(call):
        """Change the wallbox global charge mode --> set/ChargeMode [0, .., 3]."""
        topic = f"{call.data.get('mqtt_prefix')}/set/ChargeMode"
        _LOGGER.debug("topic (change_global_charge_mode): %s", topic)

        if call.data.get("global_charge_mode") == "Sofortladen":
            payload = str(0)
        elif call.data.get("global_charge_mode") == "Min+PV-Laden":
            payload = str(1)
        elif call.data.get("global_charge_mode") == "Nur PV-Laden":
            payload = str(2)
        elif call.data.get("global_charge_mode") == "Stop":
            payload = str(3)
        else:
            payload = str(4)
        hass.components.mqtt.publish(hass, topic, payload)

    def fun_change_charge_limitation_per_cp(call):
        """If box is in state 'Sofortladen', the charge limitation can be finetuned.

        --> config/set/sofort/lp/#/chargeLimitation [0, 1, 2].
        If the wallbox shall charge only a limited amount of energy [1] or to a certain SOC [2]
        --> config/set/sofort/lp/#/energyToCharge [value in kWh]
        --> config/set/sofort/lp/#/socToChargeTo [value in %].
        """
        topic = f"{call.data.get('mqtt_prefix')}/config/set/sofort/lp/{call.data.get('charge_point_id')}/chargeLimitation"
        _LOGGER.debug("topic (change_charge_limitation_per_cp): %s", topic)

        if call.data.get("charge_limitation") == "Not limited":
            payload = str(0)
            hass.components.mqtt.publish(hass, topic, payload)
        elif call.data.get("charge_limitation") == "kWh":
            payload = str(1)
            topic2 = f"{call.data.get('mqtt_prefix')}/config/set/sofort/lp/{call.data.get('charge_point_id')}/energyToCharge"
            payload2 = str(call.data.get("energy_to_charge"))
            hass.components.mqtt.publish(hass, topic, payload)
            hass.components.mqtt.publish(hass, topic2, payload2)
        elif call.data.get("charge_limitation") == "SOC":
            payload = str(2)
            topic2 = f"{call.data.get('mqtt_prefix')}/config/set/sofort/lp/{call.data.get('charge_point_id')}/socToChargeTo"
            payload2 = str(call.data.get("required_soc"))
            hass.components.mqtt.publish(hass, topic, payload)
            hass.components.mqtt.publish(hass, topic2, payload2)

    def fun_change_charge_current_per_cp(call):
        """Set the charge current per loading point --> config/set/sofort/lp/#/current [value in A]."""
        topic = f"{call.data.get('mqtt_prefix')}/config/set/sofort/lp/{call.data.get('charge_point_id')}/current"
        _LOGGER.debug("topic (fun_change_charge_current_per_cp): %s", topic)

        payload = str(call.data.get("target_current"))
        hass.components.mqtt.publish(hass, topic, payload)

    def fun_enable_disable_price_based_charging(call):
        """Enable or disable price-based charging for charge point # --> set/lp#/etBasedCharging [0,1]."""
        topic = f"{call.data.get('mqtt_prefix')}/set/lp{call.data.get('charge_point_id')}/etBasedCharging"
        _LOGGER.debug("topic (enable_disable_price_based_charging): %s", topic)

        if call.data.get("selected_status") == "On":
            payload = str(1)
            hass.components.mqtt.publish(hass, topic, payload)

        else:
            payload = str(0)
            hass.components.mqtt.publish(hass, topic, payload)

    def fun_change_pricebased_price(call):
        """Change the price for price-based charging"""
        topic = f"{call.data.get('mqtt_prefix')}/set/awattar/MaxPriceForCharging"
        _LOGGER.debug("topic (change_pricebased_price): %s", topic)
        _LOGGER.debug(f"set price to: {call.data.get('target_price')}")
        hass.components.mqtt.publish(hass, topic, call.data.get("target_price"))

    # Register our services with Home Assistant.
    hass.services.async_register(DOMAIN, "enable_disable_cp", fun_enable_disable_cp)
    hass.services.async_register(
        DOMAIN, "change_global_charge_mode", fun_change_global_charge_mode
    )
    hass.services.async_register(
        DOMAIN, "change_charge_limitation_per_cp", fun_change_charge_limitation_per_cp
    )
    hass.services.async_register(
        DOMAIN, "change_charge_current_per_cp", fun_change_charge_current_per_cp
    )
    hass.services.async_register(
        DOMAIN,
        "enable_disable_price_based_charging",
        fun_enable_disable_price_based_charging,
    )
    hass.services.async_register(
        DOMAIN,
        "change_pricebased_price",
        fun_change_pricebased_price,
    )

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload all sensor entities and services if integration is removed via UI.

    No restart of home assistant is required.
    """
    hass.services.async_remove(DOMAIN, "enable_disable_cp")
    hass.services.async_remove(DOMAIN, "change_global_charge_mode")
    hass.services.async_remove(DOMAIN, "change_charge_limitation_per_cp")
    hass.services.async_remove(DOMAIN, "change_charge_current_per_cp")
    hass.services.async_remove(DOMAIN, "enable_disable_price_based_charging")
    hass.services.async_remove(DOMAIN, "change_pricebased_price")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
