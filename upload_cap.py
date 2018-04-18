import time
import sys
import obd
import logging
from lib.db.offline import OfflineHandler
import pint
from obd.UnitsAndScaling import Unit

from lib.obd_conn import OBDConn

if __name__ == "__main__":
    pint.set_application_registry(Unit)
    OfflineHandler.load_backup(sys.argv[1])
    while not OfflineHandler.buffer.empty():
        event = OfflineHandler.buffer.get()
        event = OBDConn.create_dataobj(event)
        #OfflineHandler.save_event(event)
        if event:
            event.save()