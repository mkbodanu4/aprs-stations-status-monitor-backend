# Python IGate Status Monitor
Python-based APRS-IS service for [Simple IGate Status Monitor](https://github.com/mkbodanu4/simple-igate-status-monitor)

This app monitors APRS-IS network using configured filters and updates data in [Simple IGate Status Monitor](https://github.com/mkbodanu4/simple-igate-status-monitor) database.

More details about filters are available [HERE](http://www.aprs-is.net/javAPRSFilter.aspx).

## Running as systemd service

The app could be run as systemd service. Put code into home directory and update *igate_status_monitor.service* file with the proper path. Then copy *igate_status_monitor.service* file to systemd folder (*/etc/systemd/system/*) and start service using *systemctl* command.
