"""Xiaomi Viomi integration."""
import logging
from functools import partial

from homeassistant.components.vacuum import (
    ATTR_CLEANED_AREA,
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_RETURNING,
    SUPPORT_BATTERY,
    SUPPORT_FAN_SPEED,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_SEND_COMMAND,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STOP,
    StateVacuumEntity,
)
from homeassistant.components.xiaomi_miio.device import XiaomiMiioEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, STATE_OFF, STATE_ON
from miio import DeviceException
from miio.integrations.vacuum.viomi.viomivacuum import (
    ViomiVacuum,
    ViomiVacuumSpeed,
    ViomiVacuumStatus,
)

from .const import DEVICE_PROPERTIES

_LOGGER = logging.getLogger(__name__)

ATTR_CLEANING_TIME = "cleaning_time"
ATTR_DO_NOT_DISTURB = "do_not_disturb"
ATTR_DO_NOT_DISTURB_START = "do_not_disturb_start"
ATTR_DO_NOT_DISTURB_END = "do_not_disturb_end"
ATTR_MAIN_BRUSH_LEFT = "main_brush_left"
ATTR_SIDE_BRUSH_LEFT = "side_brush_left"
ATTR_FILTER_LEFT = "filter_left"
ATTR_MOP_LEFT = "mop_left"
ATTR_ERROR = "error"
ATTR_STATUS = "status"
ATTR_MOP_ATTACHED = "mop_attached"

SUPPORT_VIOMI = (
    SUPPORT_STATE
    | SUPPORT_PAUSE
    | SUPPORT_STOP
    | SUPPORT_RETURN_HOME
    | SUPPORT_FAN_SPEED
    | SUPPORT_SEND_COMMAND
    | SUPPORT_BATTERY
    | SUPPORT_START
)

STATE_CODE_TO_STATE = {
    0: STATE_IDLE,  # IdleNotDocked
    1: STATE_IDLE,  # Idle
    2: STATE_IDLE,  # Idle2
    3: STATE_CLEANING,  # Cleaning
    4: STATE_RETURNING,  # Returning
    5: STATE_DOCKED,  # Docked
    6: STATE_CLEANING,  # VacuumingAndMopping
}

ERRORS_FALSE_POSITIVE = (
    0,  # Sleeping and not charging
    2103,  # Charging
    2104,  # ? Returning
    2105,  # Fully charged
    2110,  # ? Cleaning
)


async def async_setup_entry(hass, config_entry: ConfigEntry, async_add_entities):
    """Set up the Xiaomi Viomi vacuum cleaner robot from a config entry."""
    entities = []

    host = config_entry.data[CONF_HOST]
    token = config_entry.data[CONF_TOKEN]
    name = config_entry.title
    unique_id = config_entry.unique_id

    # Create handler
    _LOGGER.debug("Initializing viomi with host %s (token %s...)", host, token[:5])
    vacuum = ViomiVacuum(host, token)

    viomi = ViomiVacuumIntegration(name, vacuum, config_entry, unique_id)
    entities.append(viomi)

    async_add_entities(entities, update_before_add=True)


class ViomiVacuumIntegration(XiaomiMiioEntity, StateVacuumEntity):
    """Xiaomi Viomi integration handler."""

    def __init__(self, name, device, entry, unique_id):
        """Initialize the Xiaomi vacuum cleaner robot handler."""
        super().__init__(name, device, entry, unique_id)

        self.vacuum_state = None
        self._available = False

        self.consumable_state = None
        self.dnd_state = None
        self._fan_speeds = None
        self._fan_speeds_reverse = None

    @property
    def state(self):
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
                    ATTR_STATUS: str(self._get_status()),
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
    def supported_features(self):
        """Flag vacuum cleaner robot features that are supported."""
        return SUPPORT_VIOMI

    def _got_error(self):
        error_code = self.vacuum_state.error_code
        return error_code and error_code not in ERRORS_FALSE_POSITIVE

    def _get_status(self):
        return STATE_CODE_TO_STATE[int(self.vacuum_state.state.value)]

    def _get_device_status(self):
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

            self._fan_speeds = state.fan_speed_presets()
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

    async def async_start(self):
        """Start or resume the cleaning task."""
        await self._try_command("Unable to start the vacuum: %s", self._device.start)

    async def async_pause(self):
        """Pause the cleaning task."""
        await self._try_command("Unable to set start/pause: %s", self._device.pause)

    async def async_stop(self, **kwargs):
        """Stop the vacuum cleaner."""
        await self._try_command("Unable to stop: %s", self._device.stop)

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
