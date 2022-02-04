"""Test sensor for simple integration."""
from typing import Optional

import pytest
from homeassistant.components.vacuum import (
    DOMAIN,
    SERVICE_CLEAN_SPOT,
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
    (SERVICE_CLEAN_SPOT, None, None),
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

        if method and parameters:
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
    "service,initial_state,method,parameters",
    [
        (SERVICE_START_PAUSE, None, "set_mode_withroom", [0, 1, 0]),
        (SERVICE_START_PAUSE, {"is_work": 0}, "set_mode", [0, 2]),
    ],
)
async def test_vacuum_start_stop(
    hass: HomeAssistant, service, initial_state, method, parameters
):
    entry = get_mocked_entry()
    with mocked_viomi_device(initial_state) as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()

        await hass.services.async_call(
            DOMAIN, service, {"entity_id": entity_id}, blocking=True
        )

        mock_device_send.assert_any_call(method, parameters)


@pytest.mark.parametrize(
    "speed,expected_value",
    [
        #  numeric values
        (0, ViomiVacuumSpeed.Silent.value),
        (1, ViomiVacuumSpeed.Standard.value),
        (2, ViomiVacuumSpeed.Medium.value),
        (3, ViomiVacuumSpeed.Turbo.value),
        # string values
        ("Silent", ViomiVacuumSpeed.Silent.value),
        ("Standard", ViomiVacuumSpeed.Standard.value),
        ("Medium", ViomiVacuumSpeed.Medium.value),
        ("Turbo", ViomiVacuumSpeed.Turbo.value),
        # Bad value
        (-1, None),
    ],
)
async def test_vacuum_fan_speed_service(
    hass: HomeAssistant, speed: ViomiVacuumSpeed, expected_value: Optional[int]
):
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
            {"entity_id": entity_id, "fan_speed": speed},
            blocking=True,
        )

        if expected_value is not None:
            mock_device_send.assert_any_call("set_suction", [expected_value])
        else:
            # Method wasn't called
            with pytest.raises(AssertionError):
                mock_device_send.assert_any_call("set_suction", [expected_value])


@pytest.mark.parametrize(
    "state_code,state_value",
    [
        (4, "returning"),
        (9000, None),
    ],
)
async def test_vacuum_regular_state(hass: HomeAssistant, state_code, state_value):
    entry = get_mocked_entry()
    with mocked_viomi_device({"run_state": state_code}) as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.attributes["status"] == state_value


@pytest.mark.parametrize(
    "error_code,error_value",
    [
        (502, "Low battery"),
        (9000, "Unknown error 9000"),
    ],
)
async def test_vacuum_error_state(hass: HomeAssistant, error_code, error_value):
    entry = get_mocked_entry()
    with mocked_viomi_device({"err_state": error_code}) as mock_device_send:
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.attributes["error"] == error_value
