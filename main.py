import time
import obd
import logging
from lib.db.offline import OfflineHandler
from lib.obd_conn import OBDConn

fh = logging.FileHandler("./obd.log")
fh.setFormatter(logging.Formatter('%(message)s'))
obd.logger.setLevel(obd.logging.INFO)
obd.logger.removeHandler(obd.console_handler)
obd.logger.addHandler(fh)

logging.basicConfig(level=logging.DEBUG, filename="./app.log")

if __name__ == "__main__":
    conn = OBDConn()
    try:
        OfflineHandler.start()
        while True:
            time.sleep(1)
            if not conn.connection.running:
                print("Restarted connection")
                conn.connection.start()
    except KeyboardInterrupt:
        conn.stop()
        OfflineHandler.stop()

