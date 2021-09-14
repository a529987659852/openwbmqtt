# openWBmqtt
Custom component for home assistant supporting [openWB wallbox](https://openwb.de/main/) wallbox for charging electric vehicles

## How to add this custom componant to home assistant

Clone the custom component to your custom components folder. Then, in HA, choose Settings -> Integrations -> add the Integration

The integration coding subscribes to MQTT topics `prefix/<various values>`.

The first **parameter, mqttroot**, defines the prefix that shall be applied to all MQTT topics. By default, openWB publishes data to the MQTT topic `openWB/#` (for example `openWB/lp/1/%Soc`). In this case, set the prefix to openWB and the integration will subscribe to MQTT data, for example `openWB/lp/1/%Soc`, or `openWB/global/chargeMode`, and so on.
  
If your're publishing the data from the openWB mosquitto server to another MQTT server via a bridge, the topics on the other MQTT server are usually prepended with a prefix. If this is the case, also include this prefix into the first configuration parameter, for example `somePrefix/openWB`. Then, the integration coding will subscribe to MQTT data, for example `somePrefix/openWB/global/chargeMode`, or `somePrefix/openWB/lp/1/%Soc`, and so on.

The second **parameter, chargepoints**, is the number of configured charge points. For each charge point, the integration will set up one set of sensors.

In addition, the integration also provides 4 services:
- Enable / disable a charge point
- Change the gloabl charge mode of openWB (Sofortladen, Min+PV, Nur PV, Stop, Standby)
- Change charge limitation (not limited / kWh / %SoC) per charge point incl. target values
- Change charge current per CP

Note: I provide this custom integration without any warranty. It lies in the responsability of each user to validate the functionality with his/her own openWB!
