import logging

import config
import elasticsearch
from elasticsearch_dsl import DocType, Date, Text, Integer, Float
from elasticsearch_dsl.connections import connections

try:
    connections.create_connection(hosts=config.ES_RESULT_HOSTS, timeout=20)
    tracer = logging.getLogger('elasticsearch')
    tracer.setLevel(logging.CRITICAL)  # or desired level
    tracer.addHandler(logging.FileHandler('elk.log'))

except elasticsearch.exceptions.ConnectionError:
    pass


class ECUData(DocType):
    date = Date()
    type = Text()
    value = Text()
    unit = Text()
    unit = Float()

    class Meta:
        index = 'ecudata'

    def save(self, **kwargs):
        return super().save(**kwargs)
try:
    ECUData.init()
except elasticsearch.exceptions.RequestError:
    ## Index already initalized
    pass
except elasticsearch.exceptions.ConnectionError:
    pass