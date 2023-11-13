"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant import config_entries, core
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo

from .client import CompassWifiPoolHeaterClient
from .const import DOMAIN
from .types import Device, DeviceDetail, DeviceState


class WaterTemperatureSensor(SensorEntity):
    """Representation of a water temperature sensor."""

    def __init__(self, client: CompassWifiPoolHeaterClient, device: Device) -> None:
        """Representation of a Sensor."""
        self.client = client
        self._device_id = device.unique_key
        self._attr_name = "Water Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{self._device_id}-water-temperature"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device.name,
            manufacturer="Compass",
            model=device.model_name.replace("_", " "),
        )

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        device_detail: DeviceDetail = await self.client.get_device_detail(
            self._device_id
        )
        state: DeviceState = device_detail.currentState
        self._attr_native_value = state.RMT
        self._attr_native_unit_of_measurement = (
            UnitOfTemperature.FAHRENHEIT if state.CF == 0 else UnitOfTemperature.CELSIUS
        )


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Create sensor."""
    # config = hass.data[DOMAIN][config_entry.entry_id]
    client = CompassWifiPoolHeaterClient()

    await client.connect(config_entry.data["username"], config_entry.data["password"])
    devices_list = await client.get_devices()

    async_add_entities(
        [WaterTemperatureSensor(client, device) for device in devices_list],
        update_before_add=True,
    )
