# openWBmqtt
Custom component for home assistant supporting openWB wallbox

## Example Configuration.yaml

```
openwbmqtt:
    mqttroot: 'openWB/openWB'

sensor:
  - platform: openwbmqtt
    mqttroot: 'openWB/openWB'
    chargepoints:
      - 1
```

mqttroot defines the prefix that shall be applied to all MQTT topics.

chargepoints is a list of configured charge points. For each charge point, the integration will set up one set of sensors.

