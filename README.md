# APRS Stations Status Monitor Backend 

Python-based APRS-IS data collector of APRS Stations Status Monitor.
Requires [PHP-based Frontend](https://github.com/mkbodanu4/aprs-stations-status-plugin) for database and configuration.

## Installation

1. Upload code to your VPN or server
2. Update *configuration.yaml* file with your own configuration
3. Update *assmd.service* file with the proper path to the installation folder.
4. Copy *assmd.service* file to systemd folder (*/etc/systemd/system/*)
5. Enable and start a service named *assmd*.
