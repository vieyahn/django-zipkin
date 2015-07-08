import datetime
import logging
from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

SCRIBE_HOST, SCRIBE_PORT = 'scribehost', 1463


class ScribeLogHandler(logging.Handler):
    def __init__(self, host, port, category=None):
        super(ScribeLogHandler, self).__init__()
        socket = TSocket.TSocket(host=host, port=port)
        self.transport = TTransport.TFramedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(
            trans=self.transport, strictRead=False, strictWrite=False)
        self.client = scribe.Client(iprot=protocol, oprot=protocol)
        self.category = category

    def emit(self, record):
        now = datetime.datetime.now()
        record.servertime = "%s,%0.3d" % (
            now.strftime("%Y-%m-%d %H:%M:%S"), now.microsecond / 1000
        )
        message = "\\n".join([r for r in self.format(record).split("\n") if r != ""]) + "\n"
        try:
            self.transport.open()
            entry = scribe.LogEntry(category=self.category, message=message)
            self.client.Log([entry])
            self.transport.close()
        except Exception as e:
            logging.exception(e)
