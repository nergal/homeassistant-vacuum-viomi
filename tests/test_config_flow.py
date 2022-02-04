"""Test the Xiaomi Viomi integration config flow."""
from collections import namedtuple
from unittest.mock import PropertyMock, patch

from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import (
    RESULT_TYPE_ABORT,
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
)

from custom_components.xiaomi_viomi.config_flow import CannotConnect
from custom_components.xiaomi_viomi.const import DOMAIN
from tests import TEST_HOST, TEST_MAC, TEST_MODEL, TEST_NAME, TEST_TOKEN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    flow_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert flow_result["type"] == RESULT_TYPE_FORM
    assert flow_result["errors"] is None

    device_info_mock = {"mac_address": TEST_MAC, "model": TEST_MODEL}

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        return_value=True,
    ), patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.device_info",
        new_callable=PropertyMock,
        return_value=namedtuple("ObjectName", device_info_mock.keys())(
            *device_info_mock.values()
        ),
    ), patch(
        "custom_components.xiaomi_viomi.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            flow_result["flow_id"],
            {
                "host": TEST_HOST,
                "token": TEST_TOKEN,
                "name": TEST_NAME,
            },
        )
        await hass.async_block_till_done()

        result_data = {
            "host": TEST_HOST,
            "name": TEST_NAME,
            "token": TEST_TOKEN,
            "model": TEST_MODEL,
            "mac": TEST_MAC,
        }

        assert result["type"] == RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == TEST_NAME
        assert result["data"] == result_data
        assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    flow_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        return_value=False,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow_result["flow_id"],
            {
                "host": TEST_HOST,
                "token": TEST_TOKEN,
                "name": TEST_NAME,
            },
        )

        assert result["type"] == RESULT_TYPE_FORM
        assert result["errors"] == {"base": "invalid_auth"}


async def test_form_invalid_parameters(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    flow_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        side_effect=Exception,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow_result["flow_id"],
            {
                "host": TEST_HOST,
                "token": TEST_TOKEN,
                "name": TEST_NAME,
            },
        )

        assert result["type"] == RESULT_TYPE_FORM
        assert result["errors"] == {"base": "unknown"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    flow_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            flow_result["flow_id"],
            {
                "host": TEST_HOST,
                "token": TEST_TOKEN,
                "name": TEST_NAME,
            },
        )

        assert result["type"] == RESULT_TYPE_FORM
        assert result["errors"] == {"base": "cannot_connect"}


async def test_already_configured(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    device_info_mock = {"mac_address": TEST_MAC, "model": TEST_MODEL}
    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        return_value=True,
    ), patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.device_info",
        new_callable=PropertyMock,
        return_value=namedtuple("ObjectName", device_info_mock.keys())(
            *device_info_mock.values()
        ),
    ):
        for _ in range(0, 2):
            flow_result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                flow_result["flow_id"],
                {
                    "host": TEST_HOST,
                    "token": TEST_TOKEN,
                    "name": TEST_NAME,
                },
            )

        assert result["type"] == RESULT_TYPE_ABORT
        assert result["reason"] == "already_configured"
