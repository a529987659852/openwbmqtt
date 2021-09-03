# The domain of your component. Should be equal to the name of your component.
from __future__ import annotations

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    LENGTH_KILOMETERS,
    PERCENTAGE,
    POWER_WATT,
)

from dataclasses import dataclass
from typing import Callable

# Global parameters
DOMAIN = "openwbmqtt"

MQTT_ROOT_TOPIC = 'mqttroot'
MQTT_ROOT_TOPIC_DEFAULT = 'openWB'
CHARGE_POINTS = 'chargepoints'
DEFAULT_CHARGE_POINTS = [1]

@dataclass
class openwbSensorEntityDescription(SensorEntityDescription):
    """Sensor entity description for openWB"""
    state: Callable | None = None
    valueMap: dict  | None = None

# Global sensors applying to the entire wallbox
SENSORS_GLOBAL = [
    openwbSensorEntityDescription(
        key="global/ChargeMode",
        name="Lademodus",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 0 : 'Sofortladen', 1: 'Min+PV-Laden', 2: 'PV-Laden', 3: 'Stop', 4: 'Standby'},
    ),
]

# Sensors applying to each charge point
"""
TODOs: 
- boolChargePointConfigured
- lastRfId
- boolSocManual
- pluddedladungakt
- boolSocConfigured
- AutolockCondfigured
- AutolockStatus
- boolFinishAtTimeChargeActive
"""
SENSORS_PER_LP = [
    openwbSensorEntityDescription(
        key="W",
        name="Ladeleistung (Ist)",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="energyConsumptionPer100km",
        name="Durchschnittsverbrauch (pro 100 km)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="AConfigured",
        name="Ladestrom (Soll)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kmCharged",
        name="Geladene Entfernung",
        device_class=None,
        native_unit_of_measurement=LENGTH_KILOMETERS,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:car",
    ),
    openwbSensorEntityDescription(
        key="ChargeStatus",
        name="Ladepunkt freigegeben",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
    openwbSensorEntityDescription(
        key="ChargePointEnabled",
        name="Ladepunkt aktiv",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
    openwbSensorEntityDescription(
        key="%SoC",
        name="% SoC",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kWhChargedSincePlugged",
        name="Geladene Energie (seit Anstecken)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="kWhActualCharged",
        name="Geladene Energie",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="countPhasesInUse",
        name="Anzahl der aktiven Phasen",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="boolPlugStat",
        name="Steckererkennung (angesteckt)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon="mdi:connection"
    ),
    openwbSensorEntityDescription(
        key="boolChargeStat",
        name="Steckererkennung (ladend)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon="mdi:connection"
    ),
    openwbSensorEntityDescription(
        key="boolChargeAtNight",
        name="Nachtladen aktiv",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon='mdi:weather-night'
    ),
# TODO: Conversion of time to timestamp. Currently, the remainder charge time is given as HH:MM
    openwbSensorEntityDescription(
        key="TimeRemaining",
        name="Verbleibende Ladezeit (HH:MM)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:alarm"
    ),
    openwbSensorEntityDescription(
        key="strChargePointName",
        name="Ladepunktsbezeichnung",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:form-textbox"
    ),
    openwbSensorEntityDescription(
        key="kWhDailyCharged",
        name="Geladene Energie (heute)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="boolDirectModeChargekWh",
        name="Energiemengenbegrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
    openwbSensorEntityDescription(
        key="boolDirectChargeModeSoc",
        name="SoC-Begrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
    openwbSensorEntityDescription(
        key="kWhCounter",
        name="Ladezähler",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    openwbSensorEntityDescription(
        key="PfPhase1",
        name="cos(Phi) (Phase 1)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    openwbSensorEntityDescription(
        key="PfPhase2",
        name="cos(Phi) (Phase 2)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    openwbSensorEntityDescription(
        key="PfPhase3",
        name="cos(Phi) (Phase 3)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    openwbSensorEntityDescription(
        key="VPhase1",
        name="Spannung (Phase 1)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="VPhase2",
        name="Spannung (Phase 2)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="VPhase3",
        name="Spannung (Phase 3)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="APhase1",
        name="Stromstärke (Phase 1)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    openwbSensorEntityDescription(
        key="APhase2",
        name="Stromstärke (Phase 2)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),   
    openwbSensorEntityDescription(
        key="APhase3",
        name="Stromstärke (Phase 3)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
]