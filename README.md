# homeassistant-vacuum-viomi

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/nergal/homeassistant-vacuum-viomi)


Xiaomi Viomi vacuum robot integration for Home Assistant.

> :warning: **DISCLAIMER:** This is a code that is in the early development stage, not even alpha, and it has many hardcoded stuff and was tested only on a single setup. That will be changed and refactored in upcoming commits.

## Configuration
### HACS
*TBD*
### Manual
Add the configuration to `configuration.yaml` file, like the example below:

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
| ??? | viomi.vacuum.v7 | Mi Robot Vacuum-Mop P (CN) | :warning: Assumed |
| **V-RVCLM21B** | viomi.vacuum.v6 | Viomi V2 <br> Xiaomi Viomi Cleaning Robot <br> Viomi Cleaning Robot V2 Pro | :warning: Assumed |

## Disclaimer
This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the Xiaomi Corporation,
or any of its subsidiaries or its affiliates. The official Xiaomi website can be found at https://www.mi.com/global/.

## License
This project is under the MIT license.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/nalecz)