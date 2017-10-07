import base64
import logging
from queue import Queue

import pickle
from threading import Thread

import elasticsearch


class OfflineHandler:
    buffer = Queue()
    continue_working = True
    cache_fpath = "./serialized_objects"
    worker = None

    @classmethod
    def start(cls):
        cls.worker = Thread(target=cls.work, args=())
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
        serialized_file = open(cls.cache_fpath, 'r')
        for line in serialized_file:
            ecudata = pickle.loads(line)
            cls.cache(ecudata)
        serialized_file.close()
        serialized_file = open(cls.cache_fpath, 'w')
        serialized_file.close()

    @classmethod
    def work(cls):
        while cls.continue_working or cls.buffer.not_empty:
            try:
                event = cls.buffer.get()
                try:
                    event.save()
                    print("Saved")
                except elasticsearch.exceptions.ConnectionError:
                    print("Stored")
                    cls.save_for_later(event)
            except Exception as e:
                #logging.exception(e)
                pass

