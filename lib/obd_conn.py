import datetime
import logging

import obd
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
        logging.info("Car connected")

    @staticmethod
    def on_event(event):
        if not isinstance(event.value, Status):
            cmd_type = "{}{}".format(hex(event.command.mode), hex(event.command.pid)).replace("0x", '')
            if event.value:
                try:
                    value = event.value.magnitude
                    unit = event.value.u
                except AttributeError:
                    value = "Unknown"
                    unit = event.value
                logging.debug("Event: {} TYPE: {} - Unit: {} Value: {}".format(str(event), cmd_type, magnitude, unit))
                data_obj = ECUData(
                    date=datetime.date.fromtimestamp(event.time),
                    type=cmd_type,
                    value=str(unit),
                    unit=value
                )
                OfflineHandler.cache(data_obj)

    def stop(self):
        self.connection.stop()
        self.connection.unwatch_all()
        logging.debug("Car disconnected")