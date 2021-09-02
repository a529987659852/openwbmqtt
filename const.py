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
    # DEVICE_CLASS_TIMESTAMP,
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


DOMAIN = "openwbmqtt"

MQTT_ROOT_TOPIC = 'mqttroot'
MQTT_ROOT_TOPIC_DEFAULT = 'openWB'
CHARGE_POINTS = 'chargepoints'
DEFAULT_CHARGE_POINTS = [1]


@dataclass
class DSMRReaderSensorEntityDescription(SensorEntityDescription):
    """Sensor entity description for DSMR Reader."""
    state: Callable | None = None
    valueMap: dict  | None = None


SENSORS_GLOBAL = [
    DSMRReaderSensorEntityDescription(
        key="global/ChargeMode",
        name="Lademodus",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 0 : 'Sofortladen', 1: 'Min+PV-Laden', 2: 'PV-Laden', 3: 'Stop', 4: 'Standby'},
    ),
]

SENSORS_PER_LP = [
    DSMRReaderSensorEntityDescription(
        key="W",
        name="Ladeleistung (Ist)",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=POWER_WATT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
#TODO: boolChargePointConfigured
    DSMRReaderSensorEntityDescription(
        key="energyConsumptionPer100km",
        name="Durchschnittsverbrauch (pro 100 km)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="AConfigured",
        name="Ladestrom (Soll)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="kmCharged",
        name="Geladene Entfernung",
        device_class=None,
        native_unit_of_measurement=LENGTH_KILOMETERS,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:car",
    ),
#TODO: lastRfId
    DSMRReaderSensorEntityDescription(
        key="ChargeStatus",
        name="Ladepunkt freigegeben",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
#TODO: boolSocManual
    DSMRReaderSensorEntityDescription(
        key="ChargePointEnabled",
        name="Ladepunkt aktiv",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
#TODO: pluddedladungakt
    DSMRReaderSensorEntityDescription(
        key="%SoC",
        name="% SoC",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="kWhChargedSincePlugged",
        name="Geladene Energie (seit Anstecken)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="kWhActualCharged",
        name="Geladene Energie",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="countPhasesInUse",
        name="Anzahl der aktiven Phasen",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="boolPlugStat",
        name="Steckererkennung (angesteckt)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon="mdi:connection"
    ),
    DSMRReaderSensorEntityDescription(
        key="boolChargeStat",
        name="Steckererkennung (ladend)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon="mdi:connection"
    ),
#TODO: boolSocConfigured
    DSMRReaderSensorEntityDescription(
        key="boolChargeAtNight",
        name="Nachtladen aktiv",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False},
        icon='mdi:weather-night'
    ),
# TODO: Datumskonversion (Zeit wird entweder als "x H y Min" oder "y Min" angegeben)
    DSMRReaderSensorEntityDescription(
        key="TimeRemaining",
        name="Verbleibende Ladezeit (HH:MM)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:alarm"
    ),
    DSMRReaderSensorEntityDescription(
        key="strChargePointName",
        name="Ladepunktsbezeichnung",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        icon="mdi:form-textbox"
    ),
#TODO: AutolockCondfigured
#TODO: AutolockStatus
#TODO: boolFinishAtTimeChargeActive
    DSMRReaderSensorEntityDescription(
        key="kWhDailyCharged",
        name="Geladene Energie (heute)",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
#TODO: Gibt an ob der Sofort Laden Untermodus Lademenge aktiv ist
    DSMRReaderSensorEntityDescription(
        key="boolDirectModeChargekWh",
        name="Energiemengenbegrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
#TODO: Gibt an ob der Sofort Laden Untermodus Lademenge aktiv ist
    DSMRReaderSensorEntityDescription(
        key="boolDirectChargeModeSoc",
        name="SoC-Begrenzung aktiv (Modus Sofortladen)",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=STATE_CLASS_MEASUREMENT,
        valueMap={ 1: True, 0: False}
    ),
    DSMRReaderSensorEntityDescription(
        key="kWhCounter",
        name="Ladezähler",
        device_class=DEVICE_CLASS_ENERGY,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    DSMRReaderSensorEntityDescription(
        key="PfPhase1",
        name="cos(Phi) (Phase 1)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    DSMRReaderSensorEntityDescription(
        key="PfPhase2",
        name="cos(Phi) (Phase 2)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    DSMRReaderSensorEntityDescription(
        key="PfPhase3",
        name="cos(Phi) (Phase 3)",
        device_class=DEVICE_CLASS_BATTERY,
        native_unit_of_measurement=None,
        state_class=PERCENTAGE,
    ),
    DSMRReaderSensorEntityDescription(
        key="VPhase1",
        name="Spannung (Phase 1)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
#TODO: plugStartkWh
    DSMRReaderSensorEntityDescription(
        key="VPhase2",
        name="Spannung (Phase 2)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="VPhase3",
        name="Spannung (Phase 3)",
        device_class=DEVICE_CLASS_VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="APhase1",
        name="Stromstärke (Phase 1)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    DSMRReaderSensorEntityDescription(
        key="APhase2",
        name="Stromstärke (Phase 2)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),   
    DSMRReaderSensorEntityDescription(
        key="APhase3",
        name="Stromstärke (Phase 3)",
        device_class=DEVICE_CLASS_CURRENT,
        native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
]