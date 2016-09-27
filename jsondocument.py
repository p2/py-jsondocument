#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   JSON document superclass
#
#   2014-02-05  Created by Pascal Pfiffner
#

import uuid
import logging

if __package__:
    from .jsonserver import JSONServer
else:
    from jsonserver import JSONServer


class JSONDocument(object):
    """ Base class for documents living in a NoSQL database.
    
    All CRUD methods have two versions, one where you specify the server and
    one where you rely on the document class being hooked up to a server
    already.
    
    Currently supported servers are MongoDB or Couchbase, or can be simple file
    or memory "databases".
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
            
            self.update_with(json)
        
        # set document type
        if doctype is not None:
            self.type = doctype
    
    def __getattr__(self, name):
        """ This is called when we don't yet have the attribute. """
        return None
    
    @property
    def id(self):
        return self._id
    
    def as_json(self):
        """ Return the whole document ready to be JSONified. """
        js = self.__dict__.copy()
        for key, val in js.items():
            if isinstance(val, list):
                js[key] = [j.as_json() if isinstance(j, JSONDocument) else j for j in val]
            elif isinstance(val, JSONDocument):
                js[key] = val.as_json()
        return js
    
    def for_api(self, omit=None):
        """ Return the whole OR PARTS OF the receiver, as JSON, to be consumed
        by an API.
        
        :param omit: List or set of key names to omit from the JSON; mostly
            used by superclasses
        """
        js = self.__dict__.copy()
        if omit is not None:
            for key in omit:
                if key in js:
                    del js[key]
        for key, val in js.items():
            if isinstance(val, list):
                js[key] = [j.for_api() if isinstance(j, JSONDocument) else j for j in val]
            elif isinstance(val, JSONDocument):
                js[key] = val.for_api()
        return js
    
    def __html__(self):
        """ For compatibility with other libraries, forwards to `for_api()`.
        
        This is implemented for Genshi and Django, but most importantly Jinja
        and thus Flask. """
        return self.for_api()
    
    
    # MARK: - Server
    
    @classmethod
    def assure_class_has_server(cls):
        if cls.server is None:
            raise Exception("I don't yet have a handle to the server in {}. Use `Class.hookup(JSONServer-instance)`.".format(cls))
        if cls.use_bucket is None:
            raise Exception("I don't yet have a bucket to use for class {}".format(cls))
        return cls.server

    def assure_has_server(self):
        return self.__class__.assure_class_has_server()
    
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
                raise Exception('Need a JSONServer instance but got {} with bases {}'.format(jsonsrv, jsonsrv.__class__.__bases__))
            cls.server = jsonsrv
        
        if bucket is not None and len(bucket) > 0:
            cls.use_bucket = bucket
    
    
    # MARK: - CRUD Operations
    
    def load(self):
        """ Loads the receiver's contents from database and applies the
        document's contents.
        """
        srv = self.assure_has_server()
        self.load_from(srv, self.__class__.use_bucket)
    
    def load_from(self, server, bucket=None):
        """ Loads the receiver's contents from the given server/database and
        applies the document's contents.
        """
        assert server
        if self.id is None:
            raise Exception('Need to have an id to load contents')
        
        doc = server.load_document(bucket, self.id)
        self.update_with(doc)
        
    
    def update_with(self, doc):
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
        srv = cls.assure_class_has_server()
        cls.insert_to(documents, srv, cls.use_bucket)
    
    @classmethod
    def insert_to(cls, documents, server, bucket=None):
        """ Insert one or more documents. Forwards to the specific
        implementation of the underlying NoSQL database.
        
        :param documents: Can be a single document/dictionary or a list thereof
        :param server:    The server to insert to
        
        :todo: This does NOT YET update each document's document id!!
        """
        doc_ids = server.add_documents(bucket, documents)
    
    def store(self):
        """ Store the document.
        """
        srv = self.assure_has_server()
        self.store_to(srv, self.__class__.use_bucket)
    
    def store_to(self, server, bucket=None):
        """ Store the document to the given server. Ensures that the document's
        `id` or `_id` does not change.
        
        :param server: The server to insert to
        """
        doc_id = server.store_document(bucket, self.as_json())
        if self._id is not None and str(doc_id) != str(self._id):
            raise Exception("Failed to save document, `id` doesn't match, is \"{}\", should be \"{}\"".format(doc_id, self._id))
        self._id = doc_id
    
    def remove(self):
        """ Deletes the document.
        """
        srv = self.assure_has_server()
        self.remove_from(srv, self.__class__.use_bucket)
    
    def remove_from(self, server, bucket=None):
        """ Deletes the document from the given server.
        """
        server.remove_document(bucket, self._id)
    
    @classmethod
    def find(cls, dic):
        """ Finds the documents identified by the supplied dictionary and
        instantiates documents of the receiver class, returning a list.
        
        :param dict dic: A dictionary containing the query
        :returns: A list of instances of the receiver class with documents
            matching the search criteria
        """
        srv = cls.assure_class_has_server()
        cls.find_on(dic, srv, cls.use_bucket)
    
    @classmethod
    def find_on(cls, dic, server, bucket=None):
        """ Finds the documents identified by the supplied dictionary and
        instantiates documents of the receiver class, returning a list.
        
        :param dict dic: A dictionary containing the query
        :param JSONServer server: The server to use
        :param str bucket: The bucket/collection to search in
        :returns: A list of instances of the receiver class with documents
            matching the search criteria
        """
        found = []
        docs_found = server.find(bucket, dic)
        if docs_found is not None:
            for doc in docs_found:
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

