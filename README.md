# openWBmqtt
Custom component for home assistant supporting openWB wallbox

## Example Configuration.yaml --

In order to add this custom component to home assistant, choose Settings -> Integrations -> add the Integration

The first parameter, mqttroot, defines the prefix that shall be applied to all MQTT topics.

The second parameter, chargepoints, is the number of configured charge points. For each charge point, the integration will set up one set of sensors.

