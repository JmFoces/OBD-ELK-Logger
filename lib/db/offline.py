import base64
import logging
from queue import Queue,Empty

import pickle
from threading import Thread

import elasticsearch
import pint


class OfflineHandler:
    buffer = Queue()
    continue_working = True
    cache_fpath = "./serialized_objects"
    worker = None

    @classmethod
    def start(cls):
        if not cls.worker or not cls.worker.is_alive():
            cls.worker = Thread(target=cls.work, args=(),daemon=True)
            cls.worker.start()

    @classmethod
    def stop(cls):
        cls.continue_working = False

    @classmethod
    def cache(cls, ecudata):
        cls.buffer.put(ecudata)

    @classmethod
    def save_for_later(cls, event):
        serialized_file = open(cls.cache_fpath, 'a')
        serialized = pickle.dumps(event)
        serialized_file.write(base64.b64encode(serialized) + "\n")
        serialized_file.close()

    @classmethod
    def load_all_saved(cls):
        cls.load_backup(cls.cache_fpath)
        serialized_file = open(cls.cache_fpath, 'w')
        serialized_file.close()

    @classmethod
    def load_backup(cls,fname):
        try:
            serialized_file = open(fname, 'r')
            logging.info("Connection up. Requeue saved records")
        except IOError:
            # Nothing saved for upload
            return
        for line in serialized_file:
            try:
                ecudata = pickle.loads(base64.b64decode(line))
            except (IndexError) as e:
                print(e)
                print(line)
                continue
            cls.cache(ecudata)
        serialized_file.close()

    @classmethod
    def work(cls):
        while cls.continue_working or not cls.buffer.empty():
            try:
                event = cls.buffer.get(timeout=2)
                cls.save_event(event)
            except Empty:
                continue
            except Exception as e:
                logging.exception(e)
                pass
    @classmethod
    def save_event(cls, event):
        try:
            if event:
                event.save()
            cls.load_all_saved()
        except elasticsearch.exceptions.SerializationError:
            event.value = str(event.value)
            event.save()
        except elasticsearch.exceptions.ConnectionError:
            cls.save_for_later(event)

