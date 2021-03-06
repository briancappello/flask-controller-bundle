CREATE = 'create'
DELETE = 'delete'
GET = 'get'
LIST = 'list'
PATCH = 'patch'
PUT = 'put'

ALL_METHODS = {CREATE, DELETE, GET, LIST, PATCH, PUT}
INDEX_METHODS = {CREATE, LIST}
MEMBER_METHODS = {DELETE, GET, PATCH, PUT}

_missing = type('_missing', (), {'__bool__': lambda self: False})()
