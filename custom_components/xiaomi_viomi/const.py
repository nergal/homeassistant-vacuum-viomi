"""Constants for Xiaomi Viomi integration."""

from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_IDLE,
    STATE_RETURNING,
    SUPPORT_BATTERY,
    SUPPORT_FAN_SPEED,
    SUPPORT_LOCATE,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_SEND_COMMAND,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STOP,
)

DOMAIN = "xiaomi_viomi"
CONF_FLOW_TYPE = "config_flow_device"

DEVICE_PROPERTIES = [
    "battary_life",
    "box_type",
    "cur_mapid",
    "err_state",
    "has_map",
    "has_newmap",
    "hw_info",
    "is_charge",
    "is_mop",
    "is_work",
    "light_state",
    "map_num",
    "mode",
    "mop_route",
    "mop_type",
    "remember_map",
    "repeat_state",
    "run_state",
    "s_area",
    "s_time",
    "suction_grade",
    "v_state",
    "water_grade",
    "order_time",
    "start_time",
    "water_percent",
    "zone_data",
    "sw_info",
    "main_brush_hours",
    "main_brush_life",
    "side_brush_hours",
    "side_brush_life",
    "mop_hours",
    "mop_life",
    "hypa_hours",
    "hypa_life",
]

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

ERRORS_FALSE_POSITIVE = (
    0,  # Sleeping and not charging,
    2103,  # Charging
    2104,  # ? Returning
    2105,  # Fully charged
    2110,  # ? Cleaning
)

SUPPORT_VIOMI = (
    SUPPORT_PAUSE
    | SUPPORT_STOP
    | SUPPORT_RETURN_HOME
    | SUPPORT_FAN_SPEED
    | SUPPORT_BATTERY
    | SUPPORT_SEND_COMMAND
    | SUPPORT_LOCATE
    | SUPPORT_STATE
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
