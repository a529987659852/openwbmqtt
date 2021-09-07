# openWBmqtt
Custom component for home assistant supporting openWB wallbox

## How to add this custom componant to home assistant

Clone the custom component to your custom components folder. Then, in HA, choose Settings -> Integrations -> add the Integration

The first parameter, mqttroot, defines the prefix that shall be applied to all MQTT topics.

The second parameter, chargepoints, is the number of configured charge points. For each charge point, the integration will set up one set of sensors.

In addition, the integration also provides 4 services:
- Enable / disable a charge point
- Change the gloabl charge mode of openWB (Sofortladen, Min+PV, Nur PV, Stop, Standby)
- Change charge limitation (not limited / kWh / %SoC) per charge point incl. target values
- Change charge current per CP
