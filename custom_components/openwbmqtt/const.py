"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    ENTITY_CATEGORY_CONFIG,
    ENTITY_CATEGORY_DIAGNOSTIC,
    LENGTH_KILOMETERS,
    PERCENTAGE,
    POWER_WATT,
    Platform,
)
import homeassistant.helpers.config_validation as cv

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
        name="Leistungsaufnahme (Haus)",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="pv/W",
        name="Leistungsabgabe (Haus PV)",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="evu/WhImported",
        name="Energie-Import (Haus)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) / 1000.0, 1)
    ),
    openwbSensorEntityDescription(
        key="evu/WhExported",
        name="Energie-Export (Haus)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=lambda x: round(float(x) / 1000.0, 1)
    ),
    openwbSensorEntityDescription(
        key="pv/WhCounter",
        name="Energie-Erzeugt (Haus)",
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
        name="Ladeleistung (Ist)",
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
        name="Ladestrom (Ist)",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbSensorEntityDescription(
        key="kmCharged",
        name="Geladene Entfernung",
        device_class=None,
        native_unit_of_measurement=LENGTH_KILOMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car",
    ),
    openwbSensorEntityDescription(
        key="%Soc",
        name="% SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kWhChargedSincePlugged",
        name="Geladene Energie (seit Anstecken)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: round(float(x), 1)
    ),
    openwbSensorEntityDescription(
        key="kWhActualCharged",
        name="Geladene Energie",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: round(float(x), 1)
    ),
    openwbSensorEntityDescription(
        key="countPhasesInUse",
        name="Anzahl der aktiven Phasen",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbSensorEntityDescription(
        key="TimeRemaining",
        name="Voraussichtlich vollständig geladen",
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
        key="kWhDailyCharged",
        name="Geladene Energie (heute)",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda x: round(float(x), 1)
    ),
    openwbSensorEntityDescription(
        key="kWhCounter",
        name="Ladezähler",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda x: round(float(x), 1)
    ),
    openwbSensorEntityDescription(
        key="PfPhase1",
        name="cos(Phi) (Phase 1)",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="PfPhase2",
        name="cos(Phi) (Phase 2)",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    openwbSensorEntityDescription(
        key="PfPhase3",
        name="cos(Phi) (Phase 3)",
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
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="ChargePointEnabled",
        name="Ladepunkt aktiv",
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="boolDirectModeChargekWh",
        name="Energiemengenbegrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="boolDirectChargeModeSoc",
        name="SoC-Begrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="boolChargeAtNight",
        name="Nachtladen aktiv",
        device_class=None,
        icon="mdi:weather-night",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="boolPlugStat",
        name="Steckererkennung (angesteckt)",
        device_class=None,
        icon="mdi:connection",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    openwbBinarySensorEntityDescription(
        key="boolChargeStat",
        name="Steckererkennung (ladend)",
        device_class=None,
        icon="mdi:connection",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
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
        name="Ladelimitierung",
        valueMapCurrentValue={
            0: "Keine",
            1: "Energiemenge",
            2: "SoC",
        },
        valueMapCommand={
            "Keine": 0,
            "Energiemenge": 1,
            "SoC": 2,
        },
        mqttTopicCommand="chargeLimitation",
        mqttTopicCurrentValue=None,
        modes = [
            "Keine",
            "Energiemenge",
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
    ),

]

NUMBERS_GLOBAL = [
        openWBNumberEntityDescription(
        key="minCurrentMinPv",
        name="Min+PV-Laden Stromstärke",
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
    ),
]

NUMBERS_PER_LP = [
    openWBNumberEntityDescription(
        key="current",
        name="Sofortladen Stromstärke",
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
    ),
    openWBNumberEntityDescription(
        key="energyToCharge",
        name="Lademengenbegrenzung (Energie)",
        unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        device_class='Energy',
        min_value=2.0,
        max_value=100.0,
        step=2.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        # icon=
        mqttTopicCommand="energyToCharge",
        mqttTopicCurrentValue="energyToCharge",
        mqttTopicChargeMode = "sofort",
    ),
    openWBNumberEntityDescription(
        key="socToChargeTo",
        name="Lademengenbegrenzung (SoC)",
        unit_of_measurement=PERCENTAGE,
        device_class="Battery",
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