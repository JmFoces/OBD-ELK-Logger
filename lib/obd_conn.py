import obd
from obd import Unit
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
            data_obj = ECUData(
                date=event.time,
                type="{}{}".format(chr(event.command.mode).encode("hex"), chr(event.command.pid).encode("hex")),
                value=event.value.magnitude,
                unit=str(event.value.u))
            OfflineHandler.cache(data_obj)

    def stop(self):
        self.connection.stop()
        self.connection.unwatch_all()