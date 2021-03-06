#/usr/bin/python
# coding: utf-8

import uuid
import hmac
import ujson
import hashlib
import redis

class Session(dict):
	def __init__(self, session_manager, request_handler):

		self.session_manager = session_manager
		self.request_handler = request_handler
		self.session_id = session_manager.get(self,request_handler)
	
	def save(self):
		self.session_manager.set(self,self.request_handler)


class SessionManager(object):
	def __init__(self, secret, store_options, session_timeout):
		self.secret = secret
		self.session_timeout = session_timeout
		try:
			if store_options['redis_pass']:
				self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'], password=store_options['redis_pass'])
			else:
				self.redis = redis.StrictRedis(host=store_options['redis_host'], port=store_options['redis_port'])
		except Exception as e:
			print e 
			
	# return an existed session id stored in redis server
	# and fill up the current session object  with  the  existed session data,
	# if the  session is not found in redis,generate a new one,and return it
	# 
	def get(self,session,request_handler = None):
		if (request_handler == None):
			session_id = None
		else:
			session_id = request_handler.get_secure_cookie("SID")

		if session_id == None:
			session_id = self._generate_id()
		elif  self.redis.exists(session_id):
			for key,value in ujson.loads(self.redis.get(session_id)).iteritems():
				session[key] = value
		else:
			session_id = self._generate_id()
		return session_id
	# set session id to cookie and store its value into redis	
	def set(self, session,request_handler):
		request_handler.set_secure_cookie("SID", session.session_id)

		session_data = ujson.dumps(dict(session.items()))

		self.redis.setex(session.session_id, self.session_timeout, session_data)


	def _generate_id(self):
		new_id = hashlib.sha256(self.secret + str(uuid.uuid4()))
		return new_id.hexdigest()


class InvalidSessionException(Exception):
	pass

