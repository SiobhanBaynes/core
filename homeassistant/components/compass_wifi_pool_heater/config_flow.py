"""Config flow for Compass WiFi Pool Heater integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp
import json

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
url = "https://www.captouchwifi.com/icm/api/call"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def post_request(url, payload, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            if response.status != 200:
                raise CannotConnect
            if response_json["result"] == "failed":
                raise Exception(f"Request failed: {response_json['message']}")
            response_json = await response.json()
            return response_json

async def get_token(username, password):
    payload = json.dumps({
    "action": "login",
    "username": username,
    "password": password
    })
    headers = {
    'Content-Type': 'application/json',
    }

    response = await post_request(url, payload, headers)
    return response['token']

async def get_devices(token):
    payload = json.dumps({
    "action": "getPasDevices",
    "token": token
    })
    headers = {
    'Content-Type': 'application/json',
    }

    response =  await post_request(url, payload, headers)
    return response["devices"]

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    try:
        token = await get_token(data["username"], data["password"])
    except Exception as e:
        raise InvalidAuth

    devices = await get_devices(token)

    # Return info that you want to store in the config entry.
    #return {"title": "Name of the device"}
    return devices[0]

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Compass WiFi Pool Heater."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
