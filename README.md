JSONDocument
============

`JSONDocument` can act as a superclass for classes representing models stored in JSON files.
Classes can be hooked up to `JSONServer` subclasses which makes them storeable and retrievable.
There's a working class for a **MongoDB** server and a stub implementation for a **Couchbase** server.

Checkout
--------

```bash
git clone git@github.com:p2/py-jsondocument.git jsondocument
```

Unit Tests
----------

A couple of unit tests are provided, run them like so:

```bash
python3 -m unittest jsondocument_test.py
```
