#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   A server handle
#
#   2014-03-25  Created by Pascal Pfiffner


class JSONServer(object):
    """ Abstract superclass for NoSQL-style servers.
    """
    
    def load_document(self, bucket, doc_id):
        """ Load an individual document.
        
        :param str bucket: The bucket/collection name
        :param str doc_id: The document id
        :returns: A JSON string representing the document
        """
        return None
    
    def add_documents(self, bucket, documents):
        """ Store one or more documents in the database.
        
        :param str bucket: The bucket/collection name
        :param documents: Can be a single document/dictionary or a list thereof
        :returns: A list of document ids for all created documents
        """
        return None
    
    def store_document(self, bucket, document):
        """ Store a complete document.
        
        :param str bucket: The bucket/collection name
        :param document: A complete JSON document
        :returns: The document id on success
        """
        return None
    
    def remove_document(self, bucket, doc_id):
        """ Deletes a given document.
        
        :param str bucket: The bucket/collection name
        :param str doc_id: The document id of the document to remove.
        """
        pass
    
    def find(self, bucket, dictionary):
        """ Find documents.
        
        :param str bucket: The bucket/collection name
        :param dict dictionary: The NoSQL query dictionary
        :returns: An iterable over matching results
        """
        return None

