JSONDocument
============

`JSONDocument` can act as a superclass for classes representing models stored in JSON files.
Classes can be hooked up to `JSONServer` subclasses which makes them storeable and retrievable.
There's even a working class for a **MongoDB** server and a stub implementation for a **Couchbase** server, imagine that!


Checkout
--------

```bash
git clone git@github.com:p2/py-jsondocument.git jsondocument
```

Unit Tests
----------

Since jsondocument is usually used as a module, run these tests from one level up, like so:

```bash
python -m unittest jsondocument/jsondocument_test.py
```
