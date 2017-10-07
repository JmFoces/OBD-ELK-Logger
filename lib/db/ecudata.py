import config
import elasticsearch
from elasticsearch_dsl import DocType, Date, String, Integer
from elasticsearch_dsl.connections import connections

try:
    connections.create_connection(hosts=config.ES_RESULT_HOSTS, timeout=20)
except elasticsearch.exceptions.ConnectionError:
    pass


class ECUData(DocType):
    date = Date()
    type = Integer()
    value = String()
    unit = String()

    class Meta:
        index = 'ecudata'

try:
    ECUData.init()
except elasticsearch.exceptions.RequestError:
    ## Index already initalized
    pass