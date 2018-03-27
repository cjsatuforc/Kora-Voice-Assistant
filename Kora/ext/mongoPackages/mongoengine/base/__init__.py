# Base module is split into several files for convenience. Files inside of
# this module should import from a specific submodule (e.g.
# `from mongoengine.base.document import BaseDocument`), but all of the
# other modules should import directly from the top-level module (e.g.
# `from mongoengine.base import BaseDocument`). This approach is cleaner and
# also helps with cyclical import errors.
from .common import *
from .datastructures import *
from .document import *
from .fields import *
from .metaclasses import *

__all__ = (
    # common
    'UPDATE_OPERATORS', '_document_registry', 'get_document',

    # datastructures
    'BaseDict', 'BaseList', 'EmbeddedDocumentList', 'LazyReference',

    # document
    'BaseDocument',

    # fields
    'BaseField', 'ComplexBaseField', 'ObjectIdField', 'GeoJsonBaseField',

    # metaclasses
    'DocumentMetaclass', 'TopLevelDocumentMetaclass'
)
