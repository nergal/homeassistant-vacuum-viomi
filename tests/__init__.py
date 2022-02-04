"""Tests for the Xiaomi Viomi integration."""
from typing import Any
from unittest.mock import patch

from homeassistant.components.vacuum import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaomi_viomi.const import DOMAIN as CUSTOM_DOMAIN

TEST_HOST = "1.1.1.1"
TEST_MAC = "f2:ff:ff:ff:ff:ff"
TEST_MODEL = "viomi.vacuum.v8"
TEST_TOKEN = "ffffffffffffffffffffffffffffffff"
TEST_NAME = "mocked_vacuum"

MOCKING_SEND_METHOD = "miio.integrations.vacuum.viomi.viomivacuum.ViomiVacuum.send"

MOCKED_DEVICE_STATE = {
    "battary_life": 100,
    "box_type": 1,
    "err_state": 2105,
    "has_map": 1,
    "has_newmap": 1,
    "hw_info": "1.0.3",
    "is_charge": 0,
    "is_mop": 0,
    "is_work": 1,
    "light_state": 1,
    "mode": 0,
    "mop_type": 0,
    "order_time": "0",
    "remember_map": 1,
    "repeat_state": 0,
    "run_state": 5,
    "s_area": 11.96,
    "s_time": 20,
    "start_time": 0,
    "suction_grade": 0,
    "sw_info": "3.5.3_0017",
    "v_state": 10,
    "water_grade": 12,
    "zone_data": "0",
}

MOCKED_DEVICE_INFO = {
    "model": TEST_MODEL,
    "mac": TEST_MAC,
}


def get_entity_id() -> str:
    return DOMAIN + "." + TEST_NAME


def get_mocked_entry():
    return MockConfigEntry(
        domain=CUSTOM_DOMAIN,
        title=TEST_NAME,
        data={
            "host": TEST_HOST,
            "token": TEST_TOKEN,
            "name": TEST_NAME,
            "mac": TEST_MAC,
            "model": TEST_MODEL,
        },
    )


def mocked_viomi_device():
    def _device_mock_method(command: str, parameters: Any = None):
        # Request for getting device state
        if command == "get_prop" and parameters:
            property_name = parameters[0]
            if property_name in MOCKED_DEVICE_STATE:
                return [MOCKED_DEVICE_STATE[property_name]]

            return [None]
        # Request for getting state of consumables
        elif command == "get_consumables":
            return [0] * 5
        # Request DND configuration
        elif command == "get_notdisturb":
            return [0] * 5
        # Request information about the hardware
        elif command == "miIO.info":
            return MOCKED_DEVICE_INFO

        return None

    return patch(MOCKING_SEND_METHOD, wraps=_device_mock_method)
