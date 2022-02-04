from homeassistant.components.vacuum import DOMAIN, STATE_DOCKED
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaomi_viomi import DOMAIN as PLATFORM_NAME
from custom_components.xiaomi_viomi import async_setup_entry
from tests import (
    TEST_HOST,
    TEST_MAC,
    TEST_MODEL,
    TEST_NAME,
    TEST_TOKEN,
    get_entity_id,
    mocked_viomi_device,
)


async def test_platform_setup(hass: HomeAssistant):
    config = {
        DOMAIN: [
            {
                "platform": PLATFORM_NAME,
                "host": TEST_HOST,
                "token": TEST_TOKEN,
                "name": TEST_NAME,
            }
        ]
    }

    with mocked_viomi_device():
        await async_setup_component(hass, DOMAIN, config)
        await hass.async_block_till_done()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.state == STATE_DOCKED
        assert state.name == TEST_NAME


async def test_platform_setup_without_name(hass: HomeAssistant):
    config = {
        DOMAIN: [
            {
                "platform": PLATFORM_NAME,
                "host": TEST_HOST,
                "token": TEST_TOKEN,
            }
        ]
    }

    with mocked_viomi_device():
        await async_setup_component(hass, DOMAIN, config)
        await hass.async_block_till_done()

        entity_id = get_entity_id(True)
        state = hass.states.get(entity_id)

        assert state
        assert state.state == STATE_DOCKED
        assert state.name == TEST_MODEL


async def test_setup_with_update_to_004(hass: HomeAssistant):
    config = MockConfigEntry(
        domain=PLATFORM_NAME,
        title=TEST_NAME,
        data={
            "host": TEST_HOST,
            "token": TEST_TOKEN,
            "mac": TEST_MAC,
        },
    )

    with mocked_viomi_device():
        await async_setup_entry(hass, config)
        await hass.async_block_till_done()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.name == TEST_NAME
