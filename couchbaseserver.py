#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   A Couchbase server handle to be used with JSONDocument subclasses
#
#   2014-03-25  Created by Pascal Pfiffner

from couchbase import Couchbase
from jsondocument import jsonserver


class CouchbaseServer(jsonserver.JSONServer):
    """ A Couchbase server.
    
    :todo: Re-implement!
    """
    
    def __init__(self, bucket=None):
        super().__init__()
        self.bucket = bucket
        self.handle = Couchbase.connect(bucket=bucket)
    
    def store_document(self, bucket, document):
        """ TODO: MAKE IT WORK. """
        self.handle(bucket)
        self.handle.set(document.get('_id'), document)
        return None
    
    def find(self, bucket, dictionary):
        """ TODO: needs a view name! Not working! Old! BAAAAAH!
        """
        self.handle(bucket)
        return self.handle.query(self.bucket, view_name, key=dictionary)

