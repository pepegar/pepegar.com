---
title: "Home Assistant in NixOS: A Journey"
date: 2024-09-24
tags: [home-assistant, nix]
draft: true
---

I've been running Home Assistant in NixOS for a while, here's a little status
report.

## Initial Setup

There are several ways of running Home Assitant, but I run it as a native NixOS
service, backed by a PostgreSQL.  It can be configured in the
`configuration.nix` directly:

```nix
services.postgresql = {
  enable = true;
  ensureDatabases = [ "hass" ];
  ensureUsers = [{
    name = "hass";
    ensureDBOwnership = true;
  }];
};

services.home-assistant = {
  enable = true;
  configDir = "/var/lib/hass";
  config = {
    recorder.db_url = "postgresql://@/hass";
    # ...
  };
};
```

I see Home Assistant as a timeseries db, that allows doing automations, and
provides a way of displaying data in dashboards.

## Configuring Sensors

Home Assistant comes with integrations for a lot of 

Setting up sensors for my Sonnen battery system required configuring REST
sensors to fetch data from the battery's API. Here's an example of how I set up
a solar power sensor:

```nix
rest = [
  {
    resource = "http://192.168.1.xx:80/api/v2/latestdata";
    method = "GET";
    headers = {
      User-Agent = "Home Assistant";
      Content-Type = "application/json";
      Auth-Token = "YOUR_TOKEN";
    };
    scan_interval = 60;
    sensor = [
      {
        name = "solar_power_w";
        value_template = "{{ value_json['Production_W'] }}";
        unit_of_measurement = "W";
        device_class = "power";
      }
      # Other sensors...
    ];
  }
];
```

Dealing with energy flow over time required using Home Assistant's integration
platform:

```nix
sensor = [
  {
    platform = "integration";
    source = "sensor.solar_power_w";
    name = "solar_energy_production";
    unit_prefix = "k";
    round = 2;
  }
  # Other integration sensors...
];
```

## Advanced Configurations

Handling bidirectional energy flow with the grid posed a challenge. I solved
this by creating separate sensors for consumption and return:

```nix
sensor = [
  {
    platform = "template";
    sensors = {
      grid_power_consumed = {
        value_template = "{{ [0 - states('sensor.grid_feed_in')|float, 0]|max }}";
        unit_of_measurement = "W";
        device_class = "power";
      };
      grid_power_returned = {
        value_template = "{{ [states('sensor.grid_feed_in')|float, 0]|max }}";
        unit_of_measurement = "W";
        device_class = "power";
      };
    };
  },
  {
    platform = "integration";
    source = "sensor.grid_power_consumed";
    name = "grid_energy_consumed";
    unit_prefix = "k";
    round = 2;
  },
  {
    platform = "integration";
    source = "sensor.grid_power_returned";
    name = "grid_energy_returned";
    unit_prefix = "k";
    round = 2;
  }
];
```

## Troubleshooting

I encountered issues with Home Assistant failing to restart after
`nixos-rebuild`. Debugging involved checking systemd logs:

```bash
sudo journalctl -u home-assistant -n 100
```

I also ran into "module not found" errors, particularly with `aiohomekit`. This
required adding the module to the Home Assistant configuration:

```nix
services.home-assistant = {
  enable = true;
  extraPackages = python3Packages: with python3Packages; [
    aiohomekit
    # other Python packages you might need
  ];
  # rest of your configuration
};
```

## Best Practices

Managing Home Assistant configuration in NixOS involves balancing NixOS's
declarative approach with Home Assistant's need for runtime configuration. I
found it helpful to:

1. Keep as much configuration as possible in `configuration.nix`
2. Use Home Assistant's `packages` and `customComponents` options for
   additional integrations
3. Regularly backup both NixOS and Home Assistant configurations

## Lessons Learned

This process taught me the importance of understanding both NixOS's package
management and Home Assistant's configuration structure. The declarative nature
of NixOS forced me to think more carefully about my Home Assistant setup,
resulting in a more robust and reproducible configuration.

## Conclusion

Running Home Assistant on NixOS offers a unique blend of flexibility and
reproducibility. While the learning curve can be steep, the resulting system is
well-documented, easily maintainable, and highly customizable.

## Resources

- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [NixOS Home Assistant Module](https://search.nixos.org/options?channel=unstable&from=0&size=50&sort=relevance&type=packages&query=services.home-assistant)
