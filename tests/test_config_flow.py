"""Test the Xiaomi Viomi integration config flow."""
from collections import namedtuple
from unittest.mock import PropertyMock, patch

from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import RESULT_TYPE_CREATE_ENTRY, RESULT_TYPE_FORM

from custom_components.xiaomi_viomi.config_flow import CannotConnect, InvalidAuth
from custom_components.xiaomi_viomi.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == RESULT_TYPE_FORM
    assert result["errors"] is None

    device_info_mock = {
        "model": "Name of the device",
        "mac_address": "F2:FF:FF:FF:FF:FF",
    }

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
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "token": "ffffffffffffffffffffffffffffffff",
            },
        )
        await hass.async_block_till_done()

    result_data = {
        "host": "1.1.1.1",
        "model": "Name of the device",
        "token": "ffffffffffffffffffffffffffffffff",
        "mac": "f2:ff:ff:ff:ff:ff",
    }

    assert result2["type"] == RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "Name of the device"
    assert result2["data"] == result_data
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        side_effect=InvalidAuth,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "token": "ffffffffffffffffffffffffffffffff",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.xiaomi_viomi.config_flow.ViomiDeviceHub.async_device_is_connectable",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "host": "1.1.1.1",
                "token": "ffffffffffffffffffffffffffffffff",
            },
        )

    assert result2["type"] == RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}
