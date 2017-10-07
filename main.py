import logging
import time


from lib.db.offline import OfflineHandler
from lib.obd_conn import OBDConn
if __name__ == "__main__":
    conn = OBDConn()
    try:
        OfflineHandler.start()
        while True:
            time.sleep(1)
            if not conn.connection.running:
                print
                "Restarted connection"
                conn.connection.start()
    except KeyboardInterrupt:
        conn.stop()
        OfflineHandler.stop()

