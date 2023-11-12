"""File for Compass Wifi client models."""
import json
import aiohttp

from .types import Device, DeviceDetail

from .const import COMPASS_URL

class CompassWifiPoolHeaterClient:
    """Class for the Compass Wifi Pool Heater client. Use from_input to initialize."""

    def __init__(self):
        self.token = ""

    async def post_request(self, payload, headers):
        async with aiohttp.ClientSession() as session:
            async with session.post(COMPASS_URL, headers=headers, data=payload) as response:
                if response.status != 200:
                    raise CannotConnect
                response_json = await response.json()
                if response_json["result"] == "failed":
                    raise Exception(f"Request failed: {response_json['message']}")
                return response_json

    async def connect(self, **kwargs):
        payload = json.dumps({
        "action": "login",
        "username": kwargs["username"],
        "password": kwargs["password"]
        })
        headers = {
        'Content-Type': 'application/json',
        }

        response =  await self.post_request(payload, headers)
        self.token = response['token']

    async def get_devices(self) -> list[Device]:
        payload = json.dumps({
        "action": "getPasDevices",
        "token": self.token
        })
        headers = {
        'Content-Type': 'application/json',
        }

        json_data_string = await self.post_request(payload, headers)
        list_of_devices = []
        for json_obj in json_data_string["devices"]:
            device = Device(**json_obj)
            list_of_devices.append(device)
        return list_of_devices

    async def get_device_details(self) -> list[DeviceDetail]:
        devices = await self.get_devices()

        list_of_device_details = []
        for device in devices:
            device_detail = await self.get_device_detail(device.unique_key)
            device_detail = DeviceDetail.from_json(device_detail)
            list_of_device_details.append(device_detail)

        return list_of_device_details

    async def get_device_detail(self, key):
        payload = json.dumps({
        "action": "thermostatGetDetail",
        "thermostatKey": key,
        "token": self.token
        })
        headers = {
        'Content-Type': 'application/json',
        }

        response =  await self.post_request(payload, headers)
        return response["detail"]


