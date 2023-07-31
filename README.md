# NEC Beamer

activate via `configuration.yaml`, configuration flow is acctually not supported.

```
light:       
  - platform: necbeamer
    name: "NEC Beamer"                                                         
    ip_address: "192.168.0.175"
```


NEC Beamer NP2000 is tested with this integration.
It uses the Webserver provided by this beamer to interact with it via http calls.

Acctually supported are `turn-on`, `turn-off` and `update`

