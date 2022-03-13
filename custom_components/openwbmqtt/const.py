"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass, BinarySensorEntityDescription)
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (SensorDeviceClass,
                                             SensorEntityDescription,
                                             SensorStateClass)
from homeassistant.components.switch import (DEVICE_CLASS_SWITCH,
                                             SwitchEntityDescription)
from homeassistant.const import (ELECTRIC_CURRENT_AMPERE,
                                 ELECTRIC_POTENTIAL_VOLT,
                                 ENERGY_KILO_WATT_HOUR, ENERGY_WATT_HOUR,
                                 ENTITY_CATEGORY_CONFIG,
                                 ENTITY_CATEGORY_DIAGNOSTIC, LENGTH_KILOMETERS,
                                 PERCENTAGE, POWER_WATT, Platform)

PLATFORMS = [Platform.SELECT, 
    Platform.SENSOR, 
    Platform.BINARY_SENSOR, 
    Platform.NUMBER,
    Platform.SWITCH,
    ]

# Global values
DOMAIN = "openwbmqtt"
MQTT_ROOT_TOPIC = "mqttroot"
MQTT_ROOT_TOPIC_DEFAULT = "openWB"
CHARGE_POINTS = "chargepoints"
DEFAULT_CHARGE_POINTS = 1
MANUFACTURER = 'openWB'
MODEL = 'openWB'

# Data schema required by configuration flow
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
        vol.Required(CHARGE_POINTS, default=DEFAULT_CHARGE_POINTS): cv.positive_int,
    }
)


@dataclass
class openwbSensorEntityDescription(SensorEntityDescription):
    """Enhance the sensor entity description for openWB"""
    value_fn: Callable | None = None
    valueMap: dict | None = None
    mqttTopicCurrentValue: str | None = None

@dataclass
class openwbBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Enhance the sensor entity description for openWB"""
    state: Callable | None = None
    mqttTopicCurrentValue: str | None = None

@dataclass
class openwbSelectEntityDescription(SelectEntityDescription):
    """Enhance the select entity description for openWB"""
    valueMapCommand: dict | None = None
    valueMapCurrentValue: dict | None = None
    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    modes: list | None = None

@dataclass
class openwbSwitchEntityDescription(SwitchEntityDescription):
    """Enhance the select entity description for openWB"""
    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None

@dataclass
class openWBNumberEntityDescription(NumberEntityDescription):
    """Enhance the number entity description for openWB"""
    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    mqttTopicChargeMode: str | None = None


# List of global sensors that are relevant to the entire wallbox
SENSORS_GLOBAL = [
    openwbSensorEntityDescription(
        key="system/IpAddress",
        name="IP-Adresse",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon='mdi:earth',
    ),
    openwbSensorEntityDescription(
        key="system/Version",
        name="Version",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon='mdi:folder-clock',
    ),
    openwbSensorEntityDescription(
        key="global/WHouseConsumption",
        name="Hausverbrauch",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="pv/W",
        name="PV-Leistung",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) *(-1.0))
    ),
    openwbSensorEntityDescription(
        key="evu/WhImported",
        name="Netzbezug",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) / 1000.0, 1)
    ),
    openwbSensorEntityDescription(
        key="evu/WhExported",
        name="Netzeinspeisung",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) / 1000.0, 1)
    ),
    openwbSensorEntityDescription(
        key="pv/WhCounter",
        name="PV-Gesamtertrag",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) / 1000.0, 1)
    ),
]

SENSORS_PER_LP = [
    openwbSensorEntityDescription(
        key="W",
        name="Ladeleistung",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="energyConsumptionPer100km",
        name="Durchschnittsverbrauch (pro 100 km)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="AConfigured",
        name="Ladestromvorgabe",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kmCharged",
        name="Geladene Entfernung",
        device_class=None,
        native_unit_of_measurement=LENGTH_KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:map-marker-distance",
    ),
    openwbSensorEntityDescription(
        key="%Soc",
        name="SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kWhActualCharged",
        name="Geladene Energie (akt. Ladevorgang)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        value_fn=lambda x: round(float(x), 2),
    ),
    openwbSensorEntityDescription(
        key="kWhChargedSincePlugged",
        name="Geladene Energie (seit Anstecken)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        value_fn=lambda x: round(float(x), 2),
    ),
    openwbSensorEntityDescription(
        key="kWhDailyCharged",
        name="Geladene Energie (heute)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        value_fn=lambda x: round(float(x), 2),
    ),
    openwbSensorEntityDescription(
        key="kWhCounter",
        name="Geladene Energie (gesamt)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda x: round(float(x), 1),
    ),
    openwbSensorEntityDescription(
        key="countPhasesInUse",
        name="Aktive Phasen",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="TimeRemaining",
        name="Voraus. Ladeende",
        device_class=SensorDeviceClass.TIMESTAMP,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:alarm",
    ),
    openwbSensorEntityDescription(
        key="strChargePointName",
        name="Ladepunktsbezeichnung",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:form-textbox",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="PfPhase1",
        name="Leistungsfaktor (Phase 1)",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="PfPhase2",
        name="Leistungsfaktor (Phase 2)",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="PfPhase3",
        name="Leistungsfaktor (Phase 3)",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="VPhase1",
        name="Spannung (Phase 1)",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="VPhase2",
        name="Spannung (Phase 2)",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="VPhase3",
        name="Spannung (Phase 3)",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="APhase1",
        name="Stromstärke (Phase 1)",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="APhase2",
        name="Stromstärke (Phase 2)",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="APhase3",
        name="Stromstärke (Phase 3)",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]

BINARY_SENSORS_PER_LP = [
    openwbBinarySensorEntityDescription(
        key="ChargeStatus",
        name="Ladepunkt freigegeben",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    openwbBinarySensorEntityDescription(
        key="ChargePointEnabled",
        name="Ladepunkt aktiv",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    openwbBinarySensorEntityDescription(
        key="boolDirectModeChargekWh",
        name="Begrenzung Energie (Modus Sofortladen)",
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:battery-charging",
    ),
    openwbBinarySensorEntityDescription(
        key="boolDirectChargeModeSoc",
        name="Begrenzung SoC (Modus Sofortladen)",
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        icon="mdi:battery-unknown",
    ),
    openwbBinarySensorEntityDescription(
        key="boolChargeAtNight",
        name="Nachtladen aktiv",
        device_class=None,
        icon="mdi:weather-night",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbBinarySensorEntityDescription(
        key="boolPlugStat",
        name="Ladekabel",
        device_class=BinarySensorDeviceClass.PLUG,
    ),
    openwbBinarySensorEntityDescription(
        key="boolChargeStat",
        name="Autoladestatus",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
]

SELECTS_GLOBAL = [
    openwbSelectEntityDescription( 
        key="global/ChargeMode",
        entity_category=ENTITY_CATEGORY_CONFIG,
        name="Lademodus",
        valueMapCurrentValue={
            0: "Sofortladen",
            1: "Min+PV-Laden",
            2: "PV-Laden",
            3: "Stop",
            4: "Standby",
        },
        valueMapCommand={
            "Sofortladen": 0,
            "Min+PV-Laden": 1,
            "PV-Laden": 2,
            "Stop": 3,
            "Standby": 4,
        },
        mqttTopicCommand="set/ChargeMode",
        mqttTopicCurrentValue="global/ChargeMode",
        modes = [
            "Sofortladen",
            "Min+PV-Laden",
            "PV-Laden",
            "Stop",
            "Standby"
        ],
    ),
]

SELECTS_PER_LP = [
     openwbSelectEntityDescription(
        key="chargeLimitation",
        entity_category=ENTITY_CATEGORY_CONFIG,
        name="Ladebegrenzung (Modus Sofortladen)",
        valueMapCurrentValue={
            0: "Keine",
            1: "Energie",
            2: "SoC",
        },
        valueMapCommand={
            "Keine": 0,
            "Energie": 1,
            "SoC": 2,
        },
        mqttTopicCommand="chargeLimitation",
        mqttTopicCurrentValue=None,
        modes = [
            "Keine",
            "Energie",
            "SoC",
        ],
    ),
]

SWITCHES_PER_LP = [
    openwbSwitchEntityDescription(
        key="ChargePointEnabled",
        entity_category=ENTITY_CATEGORY_CONFIG,
        name = "Ladepunkt aktiv",
        mqttTopicCommand="ChargePointEnabled",
        mqttTopicCurrentValue="ChargePointEnabled",
        device_class=DEVICE_CLASS_SWITCH,
    ),

]

NUMBERS_GLOBAL = [
        openWBNumberEntityDescription(
        key="minCurrentMinPv",
        name="Mindestladestrom (Modus Min+PV-Laden)",
        unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class='Power',
        min_value=6.0,
        max_value=16.0,
        step=1.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        # icon=
        mqttTopicCommand="minCurrentMinPv",
        mqttTopicCurrentValue="minCurrentMinPv",
        mqttTopicChargeMode = "pv",
        icon="mdi:current-ac",
    ),
]

NUMBERS_PER_LP = [
    openWBNumberEntityDescription(
        key="current",
        name="Ladestromvorgabe (Modus Sofortladen)",
        unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        device_class='Power',
        min_value=6.0,
        max_value=16.0,
        step=1.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        # icon=
        mqttTopicCommand="current",
        mqttTopicCurrentValue="current",
        mqttTopicChargeMode = "sofort",
        icon="mdi:current-ac",
    ),
    openWBNumberEntityDescription(
        key="energyToCharge",
        name="Energiebegrenzung (Modus Sofortladen)",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class='Energy',
        min_value=2.0,
        max_value=100.0,
        step=2.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        icon="mdi:battery-charging",
        mqttTopicCommand="energyToCharge",
        mqttTopicCurrentValue="energyToCharge",
        mqttTopicChargeMode = "sofort",
    ),
    openWBNumberEntityDescription(
        key="socToChargeTo",
        name="SoC-Begrenzung (Modus Sofortladen)",
        unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery-unknown",
        min_value=5.0,
        max_value=100.0,
        step=5.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        # icon=
        mqttTopicCommand="socToChargeTo",
        mqttTopicCurrentValue="socToChargeTo",
        mqttTopicChargeMode = "sofort",
    ),
]