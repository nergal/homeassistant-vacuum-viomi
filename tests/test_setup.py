from homeassistant.components.vacuum import DOMAIN, STATE_DOCKED
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.xiaomi_viomi import DOMAIN as PLATFORM_NAME
from tests import (
    TEST_HOST,
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
                "model": TEST_MODEL,
            }
        ]
    }

    with mocked_viomi_device() as mock_device_send:
        await async_setup_component(hass, DOMAIN, config)

        await hass.async_block_till_done()

        mock_device_send.reset_mock()

        entity_id = get_entity_id()
        state = hass.states.get(entity_id)

        assert state
        assert state.state == STATE_DOCKED
