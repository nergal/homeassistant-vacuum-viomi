"""Xiaomi Viomi integration."""
import logging
from functools import partial
from typing import Optional

from homeassistant.components.vacuum import ATTR_CLEANED_AREA
from homeassistant.components.vacuum import DOMAIN as PLATFORM_NAME
from homeassistant.components.vacuum import STATE_ERROR, StateVacuumEntity
from homeassistant.components.xiaomi_miio import CONF_MODEL
from homeassistant.components.xiaomi_miio.device import XiaomiMiioEntity
from homeassistant.config_entries import SOURCE_USER, ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from miio import DeviceException
from miio.click_common import command
from miio.integrations.vacuum.viomi.viomivacuum import (
    ViomiVacuum,
    ViomiVacuumSpeed,
    ViomiVacuumStatus,
)

from .config_flow import validate_input
from .const import (
    ATTR_CLEANING_TIME,
    ATTR_DO_NOT_DISTURB,
    ATTR_DO_NOT_DISTURB_END,
    ATTR_DO_NOT_DISTURB_START,
    ATTR_ERROR,
    ATTR_FILTER_LEFT,
    ATTR_MAIN_BRUSH_LEFT,
    ATTR_MOP_ATTACHED,
    ATTR_MOP_LEFT,
    ATTR_SIDE_BRUSH_LEFT,
    ATTR_STATUS,
    DEVICE_PROPERTIES,
    ERRORS_FALSE_POSITIVE,
    STATE_CODE_TO_STATE,
    SUPPORT_VIOMI,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    raw_config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the Xiaomi Viomi vacuum cleaner robot from a config entry."""

    config = await validate_input(hass, raw_config)
    entry = ConfigEntry(
        domain=PLATFORM_NAME,
        data=config,
        version=2,
        title=config[CONF_NAME],
        source=SOURCE_USER,
    )
    await async_setup_entry(hass, entry, async_add_entities)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Xiaomi Viomi config entry."""

    if CONF_MODEL not in config_entry.data:
        data = config_entry.data.copy()
        data[CONF_NAME] = config_entry.title
        data[CONF_MODEL] = config_entry.title

        hass.config_entries.async_update_entry(config_entry, data=data)

    host = config_entry.data.get(CONF_HOST)
    token = config_entry.data.get(CONF_TOKEN)
    name = config_entry.data.get(CONF_NAME, config_entry.title)

    unique_id = config_entry.unique_id

    # Create handler
    _LOGGER.debug("Initializing viomi with host %s (token %s...)", host, token[:5])
    vacuum = PatchedViomiVacuum(ip=host, token=token)

    viomi = ViomiVacuumIntegration(name, vacuum, config_entry, unique_id)
    async_add_entities([viomi], update_before_add=True)


class PatchedViomiVacuum(ViomiVacuum):
    @command()
    def locate(self):
        """Locate a device."""
        self.send("set_resetpos", [1])


class ViomiVacuumIntegration(XiaomiMiioEntity, StateVacuumEntity):
    """Xiaomi Viomi integration handler."""

    _device: PatchedViomiVacuum

    def __init__(self, name, device, entry, unique_id):
        """Initialize the Xiaomi vacuum cleaner robot handler."""
        super().__init__(name, device, entry, unique_id)

        self.vacuum_state: Optional[ViomiVacuumStatus] = None
        self._available = False

        self.consumable_state = None
        self.dnd_state = None
        self._fan_speeds = None
        self._fan_speeds_reverse = None

    @property
    def state(self) -> Optional[str]:
        """Return the status of the vacuum cleaner."""
        if self.vacuum_state is not None:
            # The vacuum reverts back to an idle state after erroring out.
            # We want to keep returning an error until it has been cleared.
            if self._got_error():
                _LOGGER.error(
                    "FAILED error_code: %s, state: %s, state_code: %s",
                    self.vacuum_state.error_code,
                    self.vacuum_state.state,
                    self.vacuum_state.state.value,
                )
                return STATE_ERROR
            try:
                return STATE_CODE_TO_STATE[int(self.vacuum_state.state.value)]
            except KeyError:
                _LOGGER.error(
                    "STATE not supported: %s, state_code: %s",
                    self.vacuum_state.state,
                    self.vacuum_state.state.value,
                )

        return None

    @property
    def battery_level(self):
        """Return the battery level of the vacuum cleaner."""
        if self.vacuum_state is not None:
            return self.vacuum_state.battery

    @property
    def fan_speed(self):
        """Return the fan speed of the vacuum cleaner."""
        if self.vacuum_state is not None:
            speed = self.vacuum_state.fanspeed.value
            if speed in self._fan_speeds_reverse:
                return self._fan_speeds_reverse[speed]

            _LOGGER.debug("Unable to find reverse for %s", speed)

            return speed

    @property
    def fan_speed_list(self):
        """Get the list of available fan speed steps of the vacuum cleaner."""
        return list(self._fan_speeds) if self._fan_speeds else []

    @property
    def extra_state_attributes(self):
        """Return the specific state attributes of this vacuum cleaner."""
        attrs = {}
        if self.vacuum_state is not None:
            attrs.update(
                {
                    ATTR_DO_NOT_DISTURB: STATE_ON
                    if self.dnd_state.enabled
                    else STATE_OFF,
                    ATTR_DO_NOT_DISTURB_START: str(self.dnd_state.start),
                    ATTR_DO_NOT_DISTURB_END: str(self.dnd_state.end),
                    # Not working --> 'Cleaning mode':
                    # STATE_ON if self.vacuum_state.in_cleaning else STATE_OFF,
                    ATTR_CLEANING_TIME: int(
                        self.vacuum_state.clean_time.total_seconds() / 60
                    ),
                    ATTR_CLEANED_AREA: int(self.vacuum_state.clean_area),
                    ATTR_MAIN_BRUSH_LEFT: int(
                        self.consumable_state.main_brush_left.total_seconds() / 3600
                    ),
                    ATTR_SIDE_BRUSH_LEFT: int(
                        self.consumable_state.side_brush_left.total_seconds() / 3600
                    ),
                    ATTR_MOP_LEFT: int(
                        (
                            self.consumable_state.mop_total - self.consumable_state.mop
                        ).total_seconds()
                        / 3600
                    ),
                    ATTR_FILTER_LEFT: int(
                        self.consumable_state.filter_left.total_seconds() / 3600
                    ),
                    ATTR_STATUS: self.state,
                    ATTR_MOP_ATTACHED: self.vacuum_state.mop_installed,
                }
            )

            if self._got_error():
                attrs[ATTR_ERROR] = self.vacuum_state.error
        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def supported_features(self) -> int:
        """Flag vacuum cleaner robot features that are supported."""
        return SUPPORT_VIOMI

    def _got_error(self) -> bool:
        error_code = self.vacuum_state.error_code if self.vacuum_state else None
        return bool(error_code and error_code not in ERRORS_FALSE_POSITIVE)

    def _get_device_status(self) -> ViomiVacuumStatus:
        """Override of miio's device.status() because of bug."""
        result = {}
        for prop in DEVICE_PROPERTIES:
            value = self._device.send("get_prop", [prop])
            result[prop] = value[0] if len(value) else None

        return ViomiVacuumStatus(result)

    def update(self):
        """Fetch state from the device."""
        try:
            state = self._get_device_status()
            self.vacuum_state = state

            self._fan_speeds = {x.name: x.value for x in list(ViomiVacuumSpeed)}
            self._fan_speeds_reverse = {v: k for k, v in self._fan_speeds.items()}

            self.consumable_state = self._device.consumable_status()
            self.dnd_state = self._device.dnd_status()

            self._available = True
        except (OSError, DeviceException) as exc:
            if self._available:
                self._available = False
                _LOGGER.warning("Got exception while fetching the state: %s", exc)

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a vacuum command handling error messages."""
        try:
            await self.hass.async_add_executor_job(partial(func, *args, **kwargs))
            return True
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            return False

    async def async_turn_on(self, **kwargs):
        """Start or resume the cleaning task."""
        await self.async_start()

    async def async_turn_off(self, **kwargs):
        """Stop the cleaning task."""
        await self.async_stop()

    async def async_toggle(self, **kwargs):
        """Start or pause depending on current state."""
        await self.async_start_pause()

    async def async_start(self):
        """Start or resume the cleaning task."""
        await self._try_command("Unable to start the vacuum: %s", self._device.start)

    async def async_pause(self):
        """Pause the cleaning task."""
        await self._try_command("Unable to set start/pause: %s", self._device.pause)

    async def async_start_pause(self):
        """Start or pause depending on current state."""
        if self.vacuum_state.is_on:
            await self.async_pause()
        else:
            await self.async_start()

    async def async_stop(self, **kwargs):
        """Stop the vacuum cleaner."""
        await self._try_command("Unable to stop: %s", self._device.stop)

    async def async_locate(self, **kwargs):
        """Locate the vacuum cleaner."""
        await self._try_command("Unable to locate: %s", self._device.locate)

    async def async_clean_spot(self, **kwargs):
        """Suppress NotImplementedError for clean spot capability."""
        pass

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        """Set fan speed."""
        if fan_speed in self._fan_speeds:
            fan_speed = ViomiVacuumSpeed(self._fan_speeds[fan_speed])
        else:
            try:
                fan_speed = ViomiVacuumSpeed(int(fan_speed))
            except ValueError as exc:
                _LOGGER.error(
                    "Fan speed step not recognized (%s). Valid speeds are: %s",
                    exc,
                    self.fan_speed_list,
                )
                return

        await self._try_command(
            "Unable to set fan speed: %s", self._device.set_fan_speed, fan_speed
        )

    async def async_return_to_base(self, **kwargs):
        """Set the vacuum cleaner to return to the dock."""
        await self._try_command("Unable to return home: %s", self._device.home)

    async def async_send_command(self, command, params=None, **kwargs):
        """Send raw command."""
        await self._try_command(
            "Unable to send command to the vacuum: %s",
            self._device.raw_command,
            command,
            params,
        )
