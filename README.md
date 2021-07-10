# Homeassistant Vacuum Viomi integration for HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/nergal/homeassistant-vacuum-viomi)


Xiaomi Viomi vacuum robot integration for Home Assistant.

> :warning: **DISCLAIMER:** This code is an early alpha release with all related consequences. If you decide to use it, any feedback is appreciated

## Installation
### HACS
Install it through HACS by adding this as a custom repository: https://github.com/nergal/homeassistant-vacuum-viomi, go to the integrations page in your configuration, click on the `Add Integration` button in the bottom right corner of a screen, and search for `Xiaomi Viomi Vacuum`.

### Manual
Copy contents of `custom_components` folder to your Home Assistant `config/custom_components` folder. Restart Home Assistant, and then the integration can be added and configured through the native integration setup. If you don't see it in the native integrations list, press Ctrl+F5 to refresh the browser while you're on that page and retry.

Also you may add the manual configuration to `configuration.yaml` file, like the example below:

```
vacuum:
  - platform: xiaomi_viomi
    host: 192.168.1.1
    token: !secret vacuum
    name: Vacuum V8
```

## Tested models
| Model | Device ID | Aliases | Status |
| ----- | --------- | ------- | ------ |
| **STYJ02YM** | viomi.vacuum.v8 | Mi Robot Vacuum-Mop P <br> MiJia Mi Robot Vacuum Cleaner <br> Xiaomi Mijia Robot Vacuum Cleaner LDS | :white_check_mark: Verified |
| **STY02YM** | viomi.vacuum.v7 | Mi Robot Vacuum-Mop P (CN) | :warning: Not tested |
| **V-RVCLM21B** | viomi.vacuum.v6 | Viomi V2 <br> Xiaomi Viomi Cleaning Robot <br> Viomi Cleaning Robot V2 Pro | :warning: Not tested |

## Disclaimer
This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the Xiaomi Corporation,
or any of its subsidiaries or its affiliates. The official Xiaomi website can be found at https://www.mi.com/global/.

## License
This project is under the MIT license.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/nalecz)
