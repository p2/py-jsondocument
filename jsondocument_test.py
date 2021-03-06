#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Run with:
#      python3 -m unittest jsondocument_test.py

import unittest
if __package__:
    from .jsondocument import JSONDocument
    from .jsonserver import JSONServer
else:
    from jsondocument import JSONDocument
    from jsonserver import JSONServer


class TestJSONDocument(unittest.TestCase):
    
    def test_hookup(self):
        """ Test hooking up a document to a server. """
        doc = JSONDocument(None, None)
        with self.assertRaises(Exception, msg="Must hook up a proper JSONServer subclass"):
            doc.__class__.hookup(WrongMockServer())
        with self.assertRaises(Exception, msg="Cannot hook up without providing a JSONServer initially"):
            doc.__class__.hookup(None, 'bucket')
        doc.__class__.hookup(MockServer())
    
    def test_init(self):
        """ Test document initialization. """
        doc = JSONDocument(None, None)
        self.assertIsNotNone(doc.id, 'Must generate a uuid on instantiation if not provided with one')
        self.assertIsNotNone(doc.as_json()['_id'], 'Must generate a uuid on instantiation if not provided with one')
        doc = JSONDocument(None, None, {'a': '1'})
        self.assertIsNotNone(doc.id, 'Must generate a uuid on instantiation if not provided with one')
        self.assertIsNotNone(doc.as_json()['_id'], 'Must generate a uuid on instantiation if not provided with one')
        doc = JSONDocument('abc', None)
        self.assertEqual('abc', doc.id, 'Must use the provided document id')
        doc = JSONDocument('abc', None, {'_id': 'def', 'id': 'xyz'})
        self.assertEqual('abc', doc.id, 'Must use the provided document id, bypassing the one in the json document')
        self.assertEqual('abc', doc.as_json()['_id'], 'Must use the provided document id, bypassing the one in the json document')
        
        doc = JSONDocument(None, None, {'_id': 'def'})
        self.assertEqual('def', doc.id, 'Must extract the document id from `_id` from the provided document')
        doc = JSONDocument(None, None, {'id': 'def'})
        self.assertEqual('def', doc.id, "Must extract the document id from the provided document even if it's `id`")
        
        doc = JSONDocument(None, 'test-document')
        self.assertEqual('test-document', doc.type, 'Must accept document type')
        doc = JSONDocument(None, 'test-document', {})
        self.assertEqual('test-document', doc.type, 'Must accept document type')
    
    def test_store_new(self):
        """ Test storing a new document without id. """
        JSONDocument.server = None
        doc = JSONDocument(None, None)
        with self.assertRaises(Exception, msg="Must raise when trying to store without server"):
            doc.store()
        doc.__class__.hookup(MockUselessServer())
        with self.assertRaises(Exception, msg="Must raise when not storing successfully"):
            doc.store()
        doc.__class__.hookup(MockServer())
        with self.assertRaises(Exception, msg="Must raise when hooked up to a server but not a bucket/collection"):
            doc.store()
        doc.__class__.hookup(MockServer(), 'foo')
        doc.store()
    
    def test_find_documents(self):
        """ Test finding documents. """
        # TODO
        pass


class MockServer(JSONServer):
    def store_document(self, bucket, document):
        return document['_id']
    
    def find(self, bucket, dict):
        return []

class MockUselessServer(JSONServer):
    pass

class WrongMockServer(object):
    pass
    
