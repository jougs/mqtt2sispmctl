# mqtt2sispmctl

A simple MQTT client for the GEMBIRD SiS-PM USB-controllable power outlets
that integrates with Home Assistant. See http://sispmctl.sourceforge.net/
for details about the underlying driver for the power bar.

## Install

mqtt2sispmctl can be installed by running something like this (as root):

```
groupadd sispmctl
useradd -r -d /srv/mqtt2sispmctl -G sispmctl mqtt2sispmctl
cd /srv
git clone https://github.com/jougs/mqtt2sispmctl
chown -R mqtt2sispmctl:mqtt2sispmctl mqtt2sispmctl
cp mqtt2sispmctl/mqtt2sispmctl.service /lib/systemd/system/
systemctl --system daemon-reload
systemctl enable mqtt2sispmctl.service
systemctl start mqtt2sispmctl.service
cp mqtt2sispmctl/60-sispmctl.rules /etc/udev/rules.d/
udevadm control --reload-rules
udevadm trigger
```
