import os
import avnet.iotconnect.sdk
from avnet.iotconnect.sdk.sdklib.dra import DraDeviceConfig, DraDeviceInfoParser, DraDiscoveryUrl, DeviceConfigError
from avnet.iotconnect.sdk.sdklib import to_json
if __name__ == '__main__':
    # unit test
    dc = DraDeviceConfig(
        platform=os.environ.get("DC_PF") or "aws",
        env=os.environ.get("DC_ENV") or "myenv",
        cpid=os.environ.get("DC_CPID") or "mycpid",
        duid=os.environ.get("DC_DUID") or "myduid"
    )


    du = DraDiscoveryUrl("https://discovery.iotconnect.io")
    print("Url = ", du.get_discovery_url(config=dc))

    print(DraDeviceInfoParser.parse_discovery_response(
        '{"d":{"ec":0,"bu":"https://diavnet.iotconnect.io/api/2.1/agent/device-identity/cg/b892c358-e375-4cc3-8841-32e271e26151","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"az"},"status":200,"message":"Success"}'
    ))

    print(to_json(DraDeviceInfoParser.parse_identity_response(
        '{"d":{"ec":0,"ct":200,"meta":{"at":2,"df":60,"cd":"7LIBDEM","gtw":null,"edge":0,"pf":1,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":1,"r":0,"ota":0},"p":{"n":"mqtt","h":"poc-iotconnect-iothub-017-eu2.azure-devices.net","p":8883,"id":"avtds-nik-deleteme","un":"poc-iotconnect-iothub-017-eu2.azure-devices.net/avtds-nik-deleteme/?api-version=2018-06-30","topics":{"rpt":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=0&$.ct=application%2Fjson&$.ce=utf-8","flt":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=3&$.ct=application%2Fjson&$.ce=utf-8","od":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=4&$.ct=application%2Fjson&$.ce=utf-8","hb":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=5&$.ct=application%2Fjson&$.ce=utf-8","ack":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=6&$.ct=application%2Fjson&$.ce=utf-8","dl":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&mt=7&$.ct=application%2Fjson&$.ce=utf-8","di":"devices/avtds-nik-deleteme/messages/events/cd=7LIBDEM&v=2.1&di=1&$.ct=application%2Fjson&$.ce=utf-8","c2d":"devices/avtds-nik-deleteme/messages/devicebound/#","set":{"pub":"$iothub/twin/PATCH/properties/reported/?$rid={version}","sub":"$iothub/twin/PATCH/properties/desired/#","pubForAll":"$iothub/twin/GET/?$rid=0","subForAll":"$iothub/twin/res/#"}}},"dt":"2024-10-29T18:57:26.730Z"},"status":200,"message":"Device info loaded successfully."}'
    )))

    print(to_json(DraDeviceInfoParser.parse_discovery_response(
        '{"d":{"ec":0,"bu":"https://awspocdi.iotconnect.io/api/2.1/agent/device-identity/cg/584af730-2854-4a77-8f3b-ca1696401e08","log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"aws","dip":1,"errorMsg":null},"status":200,"message":"Success"}'
    )))

    print(to_json(DraDeviceInfoParser.parse_identity_response(
        '{"d":{"ec":0,"ct":200,"meta":{"at":7,"df":5,"cd":"XG4EPK6","gtw":null,"edge":0,"pf":0,"hwv":"","swv":"","v":2.1},"has":{"d":0,"attr":1,"set":0,"r":0,"ota":0},"p":{"n":"mqtt","h":"a3etk4e19usyja-ats.iot.us-east-1.amazonaws.com","p":8883,"id":"avr-mchp-sn0123EE7A14329D3D01","un":"a3etk4e19usyja-ats.iot.us-east-1.amazonaws.com/avr-mchp-sn0123EE7A14329D3D01","topics":{"rpt":"$aws/rules/msg_d2c_rpt/avr-mchp-sn0123EE7A14329D3D01/2.1/0","flt":"$aws/rules/msg_d2c_flt/avr-mchp-sn0123EE7A14329D3D01/2.1/3","od":"$aws/rules/msg_d2c_od/avr-mchp-sn0123EE7A14329D3D01/2.1/4","hb":"$aws/rules/msg_d2c_hb/avr-mchp-sn0123EE7A14329D3D01/2.1/5","ack":"$aws/rules/msg_d2c_ack/avr-mchp-sn0123EE7A14329D3D01/2.1/6","dl":"$aws/rules/msg_d2c_dl/avr-mchp-sn0123EE7A14329D3D01/2.1/7","di":"$aws/rules/msg_d2c_di/avr-mchp-sn0123EE7A14329D3D01/2.1/1","c2d":"iot/avr-mchp-sn0123EE7A14329D3D01/cmd","set":{"pub":"$aws/things/avr-mchp-sn0123EE7A14329D3D01/shadow/name/setting_info/report","sub":"$aws/things/avr-mchp-sn0123EE7A14329D3D01/shadow/name/setting_info/property-shadow","pubForAll":"$aws/things/avr-mchp-sn0123EE7A14329D3D01/shadow/name/setting_info/get","subForAll":"$aws/things/avr-mchp-sn0123EE7A14329D3D01/shadow/name/setting_info/get/all"}}},"dt":"2024-10-29T19:22:03.421Z"},"status":200,"message":"Device info loaded successfully."}'
    )))

    try:
        print(to_json(DraDeviceInfoParser.parse_discovery_response(
            '{"d":{"ec":6,"bu":null,"log:mqtt":{"hn":"","un":"","pwd":"","topic":""},"pf":"aws","dip":0,"errorMsg":"CpId not found"},"status":200,"message":"CpId not found"}'
        )))
    except DeviceConfigError as ex:
        print(ex)

    try:
        print(to_json(DraDeviceInfoParser.parse_identity_response(
            '{"d":{"ec":1,"ct":200,"dt":"2024-10-29T20:10:44.382Z"},"status":200,"message":"Device info loaded successfully."}'
        )))
    except DeviceConfigError as ex:
        print(ex)
