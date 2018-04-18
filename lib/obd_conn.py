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
                except Exception as e:
                    logging.exception(e)
        logging.info("Car connected")

    @staticmethod
    def create_dataobj(event):

        if event and event.value:
            try:
                cmd_type = "{}{}".format(hex(event.command.mode), hex(event.command.pid)).replace("0x", '')
            except AttributeError:
                pass
            try:
                unit = event.value.u
                value = str(event.value.magnitude)
            except AttributeError:
                value = str(event.value)
                unit = "unknown"
            logging.debug("Event: {} TYPE: {} - Unit: {} Value: {}".format(str(event), cmd_type, value, unit))
            data_obj = ECUData(
                date=datetime.datetime.fromtimestamp(event.time),
                type=cmd_type,
                value=value,
                unit=str(unit)
            )
            return data_obj
    @staticmethod
    def on_event(event):
        if not isinstance(event.value, Status):
            data_obj = OBDConn.create_dataobj(event)
            OfflineHandler.cache(data_obj)

    def stop(self):
        self.connection.stop()
        self.connection.unwatch_all()
        logging.debug("Car disconnected")