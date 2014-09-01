#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	JSON document superclass
#
#	2014-02-05	Created by Pascal Pfiffner
#

import sys
import os.path
sys.path.insert(0, os.path.dirname(__file__))

import uuid
import logging

from jsondocument.jsonserver import JSONServer


class JSONDocument(object):
	""" Base class for documents living in a NoSQL database.
	
	Can be hooked up to JSONServer subclasses, which can represent a MongoDB or
	Couchbase server, or can be simple file or memory "databases".
	"""
	
	server = None
	use_bucket = None
	
	def __init__(self, ident, doctype=None, json=None):
		""" Initializing a document makes sure it has an id in the end by:
			- using `ident`, if provided
			- extracting `_id`, if provided in the JSON document
			- extracting `id`, if provided in the JSON document
		
		Subclasses can override this but should ALWAYS require the document id
		(which can be None) to be the first argument and accept a ``json``
		argument and contains the whole document. Intelligent initializers
		pull out ivars that they need from this document dictionary.
		"""
		# find the document id
		if ident is None:
			if json is not None:
				if '_id' in json:
					ident = json['_id']
				elif 'id' in json:
					ident = json['id']
			if ident is None:
				ident = str(uuid.uuid4())
		self._id = str(ident) if ident is not None else None
		
		# set all attributes except '_id' and 'id'
		if json is not None:
			if '_id' in json:
				del json['_id']
			if 'id' in json:
				del json['id']
			
			for key, val in json.items():
				setattr(self, key, val)
		
		# set document type
		if doctype is not None:
			self.type = doctype
	
	def __getattr__(self, name):
		""" This is called when we don't yet have the attribute. """
		return None
	
	@property
	def id(self):
		return self._id
	
	@property
	def json(self):
		return self.__dict__
	
	@property
	def api(self):
		return self.__dict__
	
	
	# -------------------------------------------------------------------------- Server
	@classmethod
	def assureServerClass(cls):
		if cls.server is None:
			raise Exception("I don't yet have a handle to the server in {}".format(cls))
		if cls.use_bucket is None:
			raise Exception("I don't yet have a bucket to use for class {}".format(cls))
		return cls.server

	def assureServer(self):
		return self.__class__.assureServerClass()
	
	@classmethod
	def hookup(cls, jsonsrv=None, bucket=None):
		""" Sets the bucket/collection to use for instances of this class.
		
		:param JSONServer jsonsrv: The JSONServer instance to hook this class
			up to
		:param str bucket: The bucket/database name to use
		"""
		if cls.server is None and jsonsrv is None:
			raise Exception('Need a JSONServer instance')
		if jsonsrv is not None:
			if not isinstance(jsonsrv, JSONServer):
				raise Exception('Need a JSONServer instance but got {} > {}'.format(jsonsrv, jsonsrv.__class__.__bases__))
			cls.server = jsonsrv
		
		if bucket is not None and len(bucket) > 0:
			cls.use_bucket = bucket
	
	@property
	def bucket(self):
		return self.__class__.use_bucket
	
	def load(self):
		""" Loads the receiver's contents from database and applies the
		document's contents.
		"""
		if self.id is None:
			raise Exception('Need to have an id to load contents')
		
		srv = self.assureServer()
		doc = srv.loadDocument(self.bucket, self.id)
		self.updateWith(doc)
	
	def updateWith(self, doc):
		""" Update the receiver's contents with the supplied document (dict).
		"""
		if doc is not None:
			for key, val in doc.items():
				try:
					setattr(self, key, val)
				except Exception as e:
					raise Exception("Failed to set attribute \"{}\": {}".format(key, e))
	
	@classmethod
	def insert(cls, documents):
		""" Insert one or more documents. Forwards to the specific
		implementation of the underlying NoSQL database.
		
		:param documents: Can be a single document/dictionary or a list thereof
		
		:todo: This does NOT YET update each document's document id!!
		"""
		srv = cls.assureServerClass()
		doc_ids = srv.addDocuments(cls.use_bucket, documents)
	
	def store(self, handle=None):
		""" Store the document.
		"""
		srv = self.assureServer()
		doc_id = srv.storeDocument(self.bucket, self.json)
		if self._id is not None and doc_id != self._id:
			raise Exception("Failed to save document, id doesn't match, is '{}', should be '{}'".format(doc_id, self._id))
		self._id = doc_id
	
	def remove(self, handle=None):
		""" Deletes the document.
		"""
		srv = self.assureServer()
		srv.removeDocument(self.bucket, self._id)
	
	@classmethod
	def find(cls, dic):
		""" Finds the documents identified by the supplied dictionary and
		instantiates documents of the receiver class, returning a list.
		
		:param dict dic: A dictionary containing the query
		:returns: A list of instances of the receiver class with documents
			matching the search criteria
		"""
		srv = cls.assureServerClass()
		found = []
		for doc in srv.find(cls.use_bucket, dic):
			found.append(cls(None, json=doc))
		
		return found


def updateDictionaryByKeyPath(dictionary, keypath, value):
	""" Update value at ``keypath``, making sure the dictionary has all the
	entries needed. If :param:`dictionary` is not a dict it creates a dict
	with :param:`dictionary` as key and ``1`` as value.
	"""
	if dictionary is None:
		dictionary = {}
	elif type(dictionary) != dict:
		dictionary = {dictionary: 1}
	
	paths = keypath.split('.')
	if len(paths) > 0:
		dd = dictionary
		last = paths.pop()
		for key in paths:
			if key not in dd or type(dd[key]) != dict:
				dd[key] = {}
			dd = dd[key]
		
		dd[last] = value
	
	return dictionary

