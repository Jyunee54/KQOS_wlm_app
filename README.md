# A sever setup for reading Wavelength Meter

This repostiory contains server script for querying wavelength data from Wavelength Meter (Highfiness WS8-2) and transmitting the data to clients.

## How to run server

Run `server.py` by following command : 
```
python3 server.py
```

## How to change Host IP and Port Number
By default, the host IP is assumed to be `127.0.0.1` (which is local host) and port number is assumed to be `65432`.
To change each configuration, refer code line at [here](https://github.com/kist-quantum/KQOS_wlm_app/blob/d7014b65fb8be3100f60488e5fb3b03d2416d9b5/server.py#L6C8-L6C21).
