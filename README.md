# ha_horoy

Home Assistant custom integration for Horoy gate control.

## Features

- `horoy_gate.list_doors`: list available doors
- `horoy_gate.open_door`: open a door by name (or by full `name+code+ekey`)

## Installation

Copy `custom_components/horoy_gate` into your Home Assistant config directory.

## Configuration (`configuration.yaml`)

```yaml
horoy_gate:
  base_url: http://horoy.ruyi.homes:8000
```

## Usage examples

### List doors

Developer Tools → Services:

- Service: `horoy_gate.list_doors`

### Open by door name

- Service: `horoy_gate.open_door`
- Data:

```yaml
name: "2B栋负一楼"
```

### Open by full payload

```yaml
name: "2B栋负一楼"
code: "4285401963"
ekey: "..."
```
