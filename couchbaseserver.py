#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   A Couchbase server handle to be used with JSONDocument subclasses
#
#   2014-03-25  Created by Pascal Pfiffner
#   2016-02-19  Start renovating

import couchbase.bucket

from jsondocument import jsonserver


class CouchbaseServer(jsonserver.JSONServer):
    """ A Couchbase server.
    """
    
    def __init__(self, couch_url):
        super().__init__()
        self.bucket = couchbase.bucket.Bucket(couch_url)
    
    def store_document(self, bucket, document):
        """ Inserts or updates the document.
        """
        ident = document['_id']
        self.bucket.upsert(ident, document)
        return ident
    
    def find(self, bucket, dictionary):
        raise Exception('Not implemented')

