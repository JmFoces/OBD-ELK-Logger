import datetime
import logging

import obd
import binascii
from obd.OBDResponse import Status

from lib.db.ecudata import ECUData
from lib.db.offline import OfflineHandler


class OBDConn:
    BAD_COMMANDS = [
        26, 27, 28
    ]

    def __init__(self):
        self.connection = obd.Async()
        for cmd_mode in [1, 2, 6]:
            for cmd in obd.commands[cmd_mode]:
                try:
                    if self.connection.supports(cmd) and cmd.pid not in self.BAD_COMMANDS:
                        self.connection.watch(cmd, callback=self.on_event)
                        print("listening for {0}".format(cmd))
                except Exception:
                    pass

    def on_event(self, event):
        if not isinstance(event.value, Status):
            logging.debug("Event: "+str(event))
            cmd_type = "{}{}".format(hex(event.command.mode), hex(event.command.pid)).replace("0x", '')
            logging.debug("TYPE: "+cmd_type)
            if event.value:
                try:
                    magnitude = event.value.magnitude
                    value = event.value.u
                except AttributeError:
                    magnitude = "Unknown"
                    value = event.value
                data_obj = ECUData(
                    date=datetime.date.fromtimestamp(event.time),
                    type=cmd_type,
                    value=str(value),
                    unit=magnitude
                )
                OfflineHandler.cache(data_obj)

    def stop(self):
        self.connection.stop()
        self.connection.unwatch_all()