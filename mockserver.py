#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   A Mock server intended for unit testing JSONDocument subclasses
#
#   2017-01-17  Created by Pascal Pfiffner

import os

if __package__:
    from .jsonserver import JSONServer
else:
    from jsonserver import JSONServer


class MockServer(JSONServer):
    """ A mock server.
    
    This class overrides the standard JSONServer methods and will pass or fail
    according to its `can_xy` and `found_documents` properties.
    """
    
    def __init__(self, host=None, port=None, database=None, bucket=None, user=None, pw=None):
        super().__init__()
        self.can_store = True
        self.can_update = True
        self.can_load = True
        self.can_remove = True
        self.found_documents = None
    
    
    # MARK: - Overrides
    
    def load_document(self, bucket, doc_id):
        if not self.can_load:
            raise Exception('Cannot load document')
    
    def add_documents(self, bucket, documents):
        if not self.can_add:
            raise Exception('Cannot add documents')
        doc_ids = []
        for doc in documents:
            if '_id' in doc:
                doc_ids.append(doc['_id'])
        return doc_ids
    
    def store_document(self, bucket, document):
        if not self.can_store:
            raise Exception('Cannot store documents')
        return document.get('_id')
    
    def remove_document(self, bucket, doc_id):
        pass
    
    def find(self, bucket, dictionary, skip=0, limit=50, sort=None, descending=False):
        return self.found_documents

