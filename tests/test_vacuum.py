"""Test sensor for simple integration."""
import pytest
from homeassistant.components.vacuum import (
    DOMAIN,
    SERVICE_LOCATE,
    SERVICE_PAUSE,
    SERVICE_RETURN_TO_BASE,
    SERVICE_SEND_COMMAND,
    SERVICE_SET_FAN_SPEED,
    SERVICE_START,
    SERVICE_START_PAUSE,
    SERVICE_STOP,
    STATE_DOCKED,
)
from homeassistant.const import SERVICE_TOGGLE, SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from miio.integrations.vacuum.viomi.viomivacuum import ViomiVacuumSpeed

from custom_components.xiaomi_viomi.const import SUPPORT_VIOMI as SUPPORT_FEATURES
from tests import get_entity_id, get_mocked_entry, mocked_viomi_device


async def test_vacuum_state(hass: HomeAssistant):
    entry = get_mocked_entry()
    with mocked_viomi_device() as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.state == STATE_DOCKED
        assert state.attributes["battery_level"] == 100
        assert state.attributes["fan_speed"] == ViomiVacuumSpeed.Silent.name
        assert state.attributes["supported_features"] == SUPPORT_FEATURES


test_service_data = [
    (SERVICE_TURN_ON, "set_mode_withroom", [0, 1, 0]),
    (SERVICE_TURN_OFF, "set_mode", [0, 0]),
    (SERVICE_TOGGLE, "set_mode_withroom", [0, 1, 0]),
    (SERVICE_START_PAUSE, "set_mode_withroom", [0, 1, 0]),
    (SERVICE_START, "set_mode_withroom", [0, 1, 0]),
    (SERVICE_PAUSE, "set_mode", [0, 2]),
    (SERVICE_RETURN_TO_BASE, "set_charge", [1]),
    (SERVICE_LOCATE, "set_resetpos", [1]),
    (SERVICE_STOP, "set_mode", [0, 0]),
]


@pytest.mark.parametrize("service,method,parameters", test_service_data)
async def test_vacuum_service(hass: HomeAssistant, service, method, parameters):
    entry = get_mocked_entry()
    with mocked_viomi_device() as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()

        await hass.services.async_call(
            DOMAIN, service, {"entity_id": entity_id}, blocking=True
        )
        mock_device_send.assert_any_call(method, parameters)


async def test_vacuum_send_command_service(hass: HomeAssistant):
    entry = get_mocked_entry()
    with mocked_viomi_device() as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()

        await hass.services.async_call(
            DOMAIN,
            SERVICE_SEND_COMMAND,
            {"command": "test_command", "entity_id": entity_id},
            blocking=True,
        )

        mock_device_send.assert_any_call("test_command", None)


@pytest.mark.parametrize(
    "speed",
    [
        ViomiVacuumSpeed.Silent,
        ViomiVacuumSpeed.Medium,
        ViomiVacuumSpeed.Standard,
        ViomiVacuumSpeed.Turbo,
    ],
)
async def test_vacuum_fan_speed_service(hass: HomeAssistant, speed: ViomiVacuumSpeed):
    entry = get_mocked_entry()
    with mocked_viomi_device() as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()

        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_FAN_SPEED,
            {"entity_id": entity_id, "fan_speed": speed.value},
            blocking=True,
        )

        mock_device_send.assert_any_call("set_suction", [speed.value])
