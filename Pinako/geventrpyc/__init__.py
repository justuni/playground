## RPyC-gevent compatibility and monkey-patching code
##
## Copyright (C) 2011 by Jiang Yio <http://inportb.com/>
##
## Includes MIT-licensed code from RPyC:
##   Copyright (c) 2005-2011
##     Tomer Filiba (tomerfiliba@gmail.com)
##     Copyrights of patches are held by their respective submitters
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

# Extended by Matthias Urlichs <matthias@urlichs.de> to eliminate busy waiting,
# and to handle client and server running in the same process. This requires
# a separate greenlet per dispatch, which doesn't exactly speed up RPyC. Sorry.

from __future__ import absolute_import

import sys, logging
from gevent import socket, spawn, event, select, hub
try:
	from gevent import ssl
except ImportError:
	pass

_rpyc = __import__('rpyc')
from rpyc.core import VoidService,Connection,Channel, consts, brine, vinegar, netref
from rpyc.core.stream import SocketStream as BaseSocketStream
from rpyc.lib.compat import next, is_py3k, select_error
from rpyc.utils.server import Server
from rpyc.utils.factory import connect_stream, _get_free_port
from rpyc.utils.registry import UDPRegistryClient

class SocketStream(BaseSocketStream):
	@classmethod
	def _connect(cls,host='0.0.0.0',port=0,family=socket.AF_INET,socktype=socket.SOCK_STREAM,proto=0,timeout=3,nodelay=False):
		s = socket.socket(family,socktype,proto)
		s.settimeout(timeout)
		s.connect((host,port))
		if nodelay:
			s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
		return s
	@classmethod
	def ssl_connect(cls,host,port,ssl_kwargs,**kwargs):
		if kwargs.pop('ipv6',False):
			kwargs['family'] = socket.AF_INET6
		s = cls._connect(host,port,**kwargs)
		s2 = ssl.wrap_socket(s,**ssl_kwargs)
		return cls(s2)

class TunneledSocketStream(SocketStream):
	__slots__ = ('tun',)
	def __init__(self,sock):
		self.sock = sock
		self.tun = None
	def close(self):
		SocketStream.close(self)
		if self.tun:
			self.tun.close()

class GeventServer(Server):
	def __init__(self,service,hostname='',ipv6=False,port=0,backlog=10,reuse_addr=True,authenticator=None,registrar=None,auto_register=None,protocol_config={},logger=None,listener=None):
		self.active = False
		self._closed = False
		self.service = service
		self.authenticator = authenticator
		self.backlog = backlog
		if auto_register is None:
			self.auto_register = bool(registrar)
		else:
			self.auto_register = auto_register
		self.protocol_config = protocol_config
		self.clients = set()
		if listener is None:
			if ipv6:
				if hostname == 'localhost' and sys.platform != 'win32':
					hostname = 'localhost6'
				self.listener = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
			else:
				self.listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			if reuse_addr and sys.platform != 'win32':
				self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			self.listener.bind((hostname,port))
		else:
			self.listener = listener
		sockname = self.listener.getsockname()
		self.host, self.port = sockname[0], sockname[1]
		if logger is None:
			logger = logging.getLogger("%s/%d" % (self.service.get_service_name(), self.port))
		self.logger = logger
		if "logger" not in self.protocol_config:
			self.protocol_config["logger"] = self.logger
		if registrar is None:
			registrar = UDPRegistryClient(logger=self.logger)
		self.registrar = registrar

	def _accept_method(self,sock):
		spawn(self._authenticate_and_serve_client,sock)

	def _serve_client(self, sock, credentials):
		addrinfo = sock.getpeername()
		h = addrinfo[0]
		p = addrinfo[1]
		if credentials:
			self.logger.info("welcome [%s]:%s (%r)", h, p, credentials)
		else:
			self.logger.info("welcome [%s]:%s", h, p)
		try:
			config = dict(self.protocol_config, credentials = credentials,
				endpoints = (sock.getsockname(), addrinfo))
			conn = GeventConnection(self.service, Channel(SocketStream(sock)),
				config = config, _lazy = True)
			conn._init_service()
			## conn.serve_all() ## _init_service() already does that
			## however, now we need to wait for it
			## this is a hack
			q = event.AsyncResult()
			def done(_):
				q.set(None)
			conn._job.link(done)
			q.get()
		finally:
			self.logger.info("goodbye [%s]:%s", h, p)

	def start(self):
		self.listener.listen(self.backlog)
		self.logger.info("server started on [%s]:%s", self.host, self.port)
		self.active = True
		if self.auto_register:
			spawn(self._bg_register)
		#self.listener.settimeout(0.5)
		try:
			while True:
				self.accept()
		except EOFError:
			return
		finally:
			self.logger.info('server has terminated')
			self.close()

class GeventConnection(Connection):
	"""Work around concurrency problems in rpyc"""
	_job = None

	def _init_service(self):
		super(GeventConnection,self)._init_service()
		if self._job is None or self._job.ready():
			self._job = spawn(self.serve_all)

	def _cleanup(self, _anyway = True):
		if self._job is not None and not self._job.ready() and self._job is not hub.getcurrent():
			self._job.kill()
		self._job = None
		super(GeventConnection,self)._cleanup(_anyway)
		
	def _dispatch_reply(self, seq, raw):
		"""There are no sync callbacks any more"""
		obj = self._unbox(raw)
		self._async_callbacks.pop(seq)(False, obj)

	def _dispatch_exception(self, seq, raw):
		obj = vinegar.load(raw,
			import_custom_exceptions = self._config["import_custom_exceptions"],
			instantiate_custom_exceptions = self._config["instantiate_custom_exceptions"],
			instantiate_oldstyle_exceptions = self._config["instantiate_oldstyle_exceptions"])
		self._async_callbacks.pop(seq)(True, obj)

	def _dispatch(self, data):
		"""Always serve in a separate greenlet. Callbacks can arrive at any time."""
		spawn(super(GeventConnection,self)._dispatch,data)
	
	def _send_request(self, handler, args, seq=None):
		if seq is None:
			seq = next(self._seqcounter)
		#print >>sys.stderr,"out REQ",seq,args
		self._send(consts.MSG_REQUEST, seq, (handler, self._box(args)))
		return seq

	def _recv(self, timeout, wait_for_lock):
		try:
			data = self._channel.recv()
		except EOFError:
			self.close()
			raise
		return data

	@staticmethod
	def _gen_reply(q):
		def reply(a,b):
			q.set((a,b))
		return reply

	def sync_request(self, handler, *args):
		"""Sends a synchronous request (waits for the reply to arrive)
		
		:raises: any exception that the requets may be generated
		:returns: the result of the request
		"""
		seq = next(self._seqcounter)
		q = event.AsyncResult()
		self._async_callbacks[seq] = self._gen_reply(q)
		seq = self._send_request(handler, args, seq=seq)
		isexc, obj = q.get()
		if isexc:
			raise obj
		else:
			return obj

	def _async_request(self, handler, args = (), callback = (lambda a, b: None)):
		seq = next(self._seqcounter)
		self._async_callbacks[seq] = callback
		seq = self._send_request(handler, args, seq=seq)

	def serve_all(self):
		"""Serves all requests and replies for as long as the connection is 
		alive."""
		try:
			while True:
				self.serve(None)
		except (socket.error, select_error, IOError):
			if not self.closed:
				raise
		except EOFError:
			pass
			
		finally:
			self.close()


def connect(host,port,service=VoidService,config={},ipv6=False):
	return connect_stream(SocketStream.connect(host,port,ipv6=ipv6),service,config)
def tlslite_connect(host,port,username,password,service=VoidService,config={},ipv6=False):
	return connect_stream(SocketStream.tlslite_connect(host,port,username,password,ipv6=ipv6),service,config)
def ssl_connect(host,port,keyfile=None,certfile=None,ca_certs=None,ssl_version=None,service=VoidService,config={},ipv6=False):
	ssl_kwargs = {'server_side':False}
	if keyfile:
		ssl_kwargs['keyfile'] = keyfile
	if certfile:
		ssl_kwargs['certfile'] = certfile
	if ca_certs:
		ssl_kwargs['ca_certs'] = ca_certs
	if ssl_version:
		ssl_kwargs['ssl_version'] = ssl_version
	else:
		ssl_kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1
	s = SocketStream.ssl_connect(host,port,ssl_kwargs,ipv6 = ipv6)
	return connect_stream(s,service,config)
def ssh_connect(sshctx,remote_port,service=VoidService,config={}):
	loc_port = _get_free_port()
	tun = sshctx.tunnel(loc_port,remote_port)
	stream = TunneledSocketStream.connect('localhost',loc_port)
	stream.tun = tun
	return Connection(service,Channel(stream),config=config)

def patch_select():
	__import__('rpyc.lib.compat')
	__import__('rpyc.core.protocol')
	_rpyc.lib.compat.select = select
	_rpyc.core.protocol.select = select
def patch_connection():
	__import__('rpyc.core')
	__import__('rpyc.core.protocol')
	__import__('rpyc.utils.factory')
	__import__('rpyc.utils.server')
	_rpyc.core.Connection = GeventConnection
	_rpyc.core.protocol.Connection = GeventConnection
	_rpyc.utils.factory.Connection = GeventConnection
	_rpyc.utils.server.Connection = GeventConnection
def patch_stream():
	__import__('rpyc.core.stream')
	_rpyc.core.stream.SocketStream = SocketStream
	_rpyc.core.stream.TunneledSocketStream = TunneledSocketStream
def patch_factory():
	__import__('rpyc.utils.factory')
	_rpyc.utils.factory.connect = connect
	_rpyc.utils.factory.tlslite_connect = tlslite_connect
	_rpyc.utils.factory.ssl_connect = ssl_connect
	_rpyc.utils.factory.ssh_connect = ssh_connect
def patch_server():
	__import__('rpyc.utils.server')
	_rpyc.utils.server.ThreadedServer = GeventServer
def patch_all(select=True,stream=True,factory=True,server=True,connection=True):
	if select:
		patch_select()
	if stream:
		patch_stream()
	if factory:
		patch_factory()
	if server:
		patch_server()
	if connection:
		patch_connection()

__all__ = ['SocketStream','TunneledSocketStream','GeventServer','connect','tlslite_connect','ssl_connect','ssh_connect','patch_select','patch_stream','patch_factory','patch_server','patch_all']
