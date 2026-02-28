# ha_horoy

Home Assistant custom integration for Horoy gate control.

## What it does

This integration discovers doors from Horoy API and exposes **each door as a Button device/entity** in Home Assistant.
Pressing the button opens that specific door.

## Installation

Copy `custom_components/horoy_gate` into your Home Assistant config directory.

## Configuration (`configuration.yaml`)

```yaml
horoy_gate:
  base_url: http://horoy.ruyi.homes:8000
```

## Usage

After Home Assistant restarts:

1. Go to **Settings → Devices & Services** (or Entities)
2. Find entities under integration domain `horoy_gate`
3. Each door appears as its own button entity/device
4. Press the button to open that door
