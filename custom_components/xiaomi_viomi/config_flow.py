"""Config flow to configure Xiaomi Viomi."""
import logging
import voluptuous as vol
from construct.core import ChecksumError
from miio import DeviceException, ViomiVacuum
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.device_registry import format_mac
from .const import CONF_MODEL, CONF_MAC, DOMAIN, MODELS_VACUUM


_LOGGER = logging.getLogger(__name__)

DEVICE_CONFIG = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
}
DEVICE_MODEL_CONFIG = vol.Schema({vol.Required(CONF_MODEL): vol.In(MODELS_VACUUM)})


class ConnectViomiDevice:
    """Class to async connect to a Viomi Device."""

    def __init__(self, hass):
        """Initialize the entity."""
        self._hass = hass
        self._device = None
        self._device_info = None

    @property
    def device(self):
        """Return the class containing all connections to the device."""
        return self._device

    @property
    def device_info(self):
        """Return the class containing device info."""
        return self._device_info

    async def async_connect_device(self, host, token):
        """Connect to the Xiaomi Device."""
        _LOGGER.debug("Initializing with host %s (token %s...)", host, token[:5])

        try:
            self._device = ViomiVacuum(host, token)
            # get the device info
            self._device_info = await self._hass.async_add_executor_job(
                self._device.info
            )
        except DeviceException as error:
            if isinstance(error.__cause__, ChecksumError):
                raise ConfigEntryAuthFailed(error) from error

            _LOGGER.error(
                "DeviceException during setup of xiaomi " + "device with host %s: %s",
                host,
                error,
            )
            return False

        _LOGGER.debug(
            "%s %s %s detected",
            self._device_info.model,
            self._device_info.firmware_version,
            self._device_info.hardware_version,
        )
        return True


class XiaomiViomiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a Xiaomi Viomi config flow."""

    VERSION = 1

    def __init__(self):
        """Set initial values for config flow."""
        self.name = None
        self.host = None
        self.token = None
        self.mac = None
        self.model = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_manual(user_input)

    async def async_step_manual(self, user_input=None):
        """First step is getting user input configuration params."""
        errors = {}
        if user_input is not None:
            self.token = user_input[CONF_TOKEN]
            self.host = user_input[CONF_HOST]

            if self.host is None or self.token is None:
                return self.async_abort(reason="incomplete_info")

            connect_device_class = ConnectViomiDevice(self.hass)
            await connect_device_class.async_connect_device(self.host, self.token)
            device_info = connect_device_class.device_info

            if self.model is None and device_info is not None:
                self.model = device_info.model

            if self.model is None:
                errors["base"] = "cannot_connect"
                return self.async_abort(reason="cannot_connect")

            if self.mac is None and device_info is not None:
                self.mac = format_mac(device_info.mac_address)

            unique_id = self.mac
            existing_entry = await self.async_set_unique_id(
                unique_id, raise_on_progress=False
            )
            if existing_entry:
                data = existing_entry.data.copy()
                data[CONF_HOST] = self.host
                data[CONF_TOKEN] = self.token

                self.hass.config_entries.async_update_entry(existing_entry, data=data)
                await self.hass.config_entries.async_reload(existing_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            if self.name is None:
                self.name = self.model

            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_HOST: self.host,
                    CONF_TOKEN: self.token,
                    CONF_MODEL: self.model,
                    CONF_MAC: self.mac,
                },
            )

        return self.async_show_form(
            step_id="manual", data_schema=DEVICE_CONFIG, errors=errors
        )
