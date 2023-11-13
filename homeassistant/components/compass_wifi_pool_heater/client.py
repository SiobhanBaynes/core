"""File for Compass Wifi client models."""
import json

import aiohttp

from .const import COMPASS_URL
from .types import Device, DeviceDetail, CannotConnect

class CompassWifiPoolHeaterClient:
    """Class for the Compass Wifi Pool Heater client. Use from_input to initialize."""

    def __init__(self) -> None:
        """Construct the class."""
        self.token = ""

    async def post_request(self, payload, headers):
        """Post request to Compass Wifi API."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                COMPASS_URL, headers=headers, data=payload
            ) as response:
                if response.status != 200:
                    raise CannotConnect
                response_json = await response.json()
                if response_json["result"] == "failed":
                    raise Exception(f"Request failed: {response_json['message']}")
                return response_json

    async def connect(self, username, password):
        """Connect to Compass Wifi API."""
        payload = json.dumps(
            {
                "action": "login",
                "username": username,
                "password": password,
            }
        )
        headers = {
            "Content-Type": "application/json",
        }

        response = await self.post_request(payload, headers)
        self.token = response["token"]

    async def get_devices(self) -> list[Device]:
        """Get devices from Compass Wifi API."""
        payload = json.dumps({"action": "getPasDevices", "token": self.token})
        headers = {
            "Content-Type": "application/json",
        }

        json_data_string = await self.post_request(payload, headers)
        list_of_devices = []
        for json_obj in json_data_string["devices"]:
            device = Device(**json_obj)
            list_of_devices.append(device)
        return list_of_devices

    async def get_device_details(self) -> list[DeviceDetail]:
        """Get device details from Compass Wifi API."""
        devices = await self.get_devices()

        list_of_device_details = []
        for device in devices:
            device_detail = await self.get_device_detail(device.unique_key)
            device_detail = DeviceDetail.from_json(device_detail)
            list_of_device_details.append(device_detail)

        return list_of_device_details

    async def get_device_detail(self, key) -> DeviceDetail:
        """Get device detail from Compass Wifi API."""
        payload = json.dumps(
            {"action": "thermostatGetDetail", "thermostatKey": key, "token": self.token}
        )
        headers = {
            "Content-Type": "application/json",
        }

        response = await self.post_request(payload, headers)
        device_detail = DeviceDetail.from_json(response["detail"])
        return device_detail
