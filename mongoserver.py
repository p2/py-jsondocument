#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	A Mongo database handle to be used with JSONDocument subclasses
#
#	2014-03-25	Created by Pascal Pfiffner

import os

from pymongo import MongoClient
from bson.objectid import ObjectId 
from jsondocument import jsonserver


class MongoServer(jsonserver.JSONServer):
	""" A MongoDB server.
	
	This class will make sure that a document's **_id** is an ``ObjectId`` if
	the document does not yet have one or if it has one that but it's
	represented as a string.
	"""
	
	def __init__(self, host=None, port=None, database=None, bucket=None, user=None, pw=None):
		super().__init__()
		if host is None:
			host = os.environ.get('MONGO_HOST', 'localhost')
		if port is None:
			port = int(os.environ.get('MONGO_PORT', 27017))
		
		conn = MongoClient(host=host, port=port)
		
		# select database
		if database is None:
			database = os.environ.get('MONGO_DB', 'default')
		self.conn = conn[database if database else 'default']
		
		# authenticate
		if user is None:
			user = os.environ.get('MONGO_USER')
		if pw is None:
			pw = os.environ.get('MONGO_PASS')
		if user and pw:
			self.conn.authenticate(user, pw)
	
	def loadDocument(self, bucket, doc_id):
		if not doc_id:
			raise Exception('Need a doc_id to load a document')
		if ObjectId.is_valid(doc_id):
			doc_id = ObjectId(doc_id)
		handle = self.handle(bucket)
		return handle.find_one(doc_id)
	
	def addDocuments(self, bucket, documents):
		for doc in documents:
			if '_id' in doc and ObjectId.is_valid(doc['_id']):
				doc['_id'] = ObjectId(doc['_id'])
		
		handle = self.handle(bucket)
		doc_ids = handle.insert(documents)
		if doc_ids is not None and list != type(doc_ids):
			doc_ids = [doc_ids]
		return doc_ids
	
	def storeDocument(self, bucket, document):
		handle = self.handle(bucket)
		if '_id' in document and ObjectId.is_valid(document['_id']):
			document['_id'] = ObjectId(document['_id'])
		return handle.save(document, manipulate=True)
	
	def removeDocument(self, bucket, doc_id):
		""" pymongo's `remove` connection method would allow to specify ``None``
		as parameter, resulting in **all documents** in the collection to be
		deleted. We're not allowing this use for now. """
		if not doc_id:
			raise Exception('Need a doc_id to remove a document')
		if ObjectId.is_valid(doc_id):
			doc_id = ObjectId(doc_id)
		handle = self.handle(bucket)
		handle.remove(spec_or_id=doc_id)
	
	def find(self, bucket, dictionary):
		handle = self.handle(bucket)
		return handle.find(dictionary)

