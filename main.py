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
    try:
        conn = OBDConn()
        OfflineHandler.start()
        while True:
            if not conn.connection.running:
                print("Restarted connection")
                conn.stop() ## Ensure lib's threads are stopped.
                del conn
                conn = OBDConn()
                conn.connection.start()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping all stuff...")
        conn.stop()
        OfflineHandler.stop()


