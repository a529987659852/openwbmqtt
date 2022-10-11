# openwbmqtt

THIS is an fork based on the work of https://github.com/a529987659852/openwbmqtt! 

Note: I provide this custom integration without any warranty. It lies in the responsability of each user to validate the functionality with his/her own openWB!

Custom component for home assistant supporting [openWB wallbox](https://openwb.de/main/) wallbox for charging electric vehicles. The integration subscribes to MQTT topics `prefix/<various values>` which are used by openwb to broadcast information and displays this informations as sensor entities.
In addition, the integration provides services that execute actions on the openwb (for example enable/disable a charge point).

If you need help, also have a look here: http://tech-engineering.de/home-assistant-und-openwb/

# How to add this custom component to home assistant

## Step 1: Deploy the Integration Coding to HA
### Option 1: Via HACS
Make sure you have [HACS](https://github.com/hacs/integration) installed. Under HACS, choose Integrations. Add this repository as a user-defined repository.

### Option 2: Manually
## Step 1: Clone component
Clone the custom component to your custom components folder.

## Step 2: Restart HA
Restart your HA instance as usual.

## Step 3: Add the Integration
In HA, choose Settings -> Integrations -> Add Integration to add the integration. HA will display a configuration window. For details, see next section. If the integration is not displayed, it may help to refresh your browser cache.

# Configuration of the Integration and Additional Information
The integration subscribes to MQTT topics `prefix/<various values>` which are used by openwb to broadcast information.

The first parameter, **mqttroot**, defines the prefix that shall be applied to all MQTT topics. By default, openWB publishes data to the MQTT topic `openWB/#` (for example `openWB/lp/1/%Soc`). In this case, set the prefix to openWB and the integration will subscribe to MQTT data coming from openWB, for example `openWB/lp/1/%Soc`, or `openWB/global/chargeMode`, and so on.
  
The second parameter, **chargepoints**, is the number of configured charge points. For each charge point, the integration will set up one set of sensors.

# Mosquitto Configuration in an Internal Network

If you're in an internal network, for example your home network, you can simply subscribe the openWB mosquitto server with the mosquitto server you're using with home assistant. No bridge is required. Instead, add the following to the configuration (for example in /etc/mosquitto/conf.d/openwb.conf):

```
#
# bridge to openWB Wallbox
#
connection openwb
address openwb.fritz.box:1883
start_type automatic
topic openWB/# both 2
local_clientid openwb.mosquitto
try_private false
cleansession true
```
If using the mqtt configuration above, **mqttroot** is `openWB` (this is the default value). Don't add a '/'.

If your're publishing the data from the openWB mosquitto server to another MQTT server via a bridge, the topics on the other MQTT server are usually prepended with a prefix. If this is the case, also include this prefix into the first configuration parameter, for example `somePrefix/openWB`. Then, the integration coding will subscribe to MQTT data comfing from MQTT, for example `somePrefix/openWB/global/chargeMode`, or `somePrefix/openWB/lp/1/%Soc`, and so on.
