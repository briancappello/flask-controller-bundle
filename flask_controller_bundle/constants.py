CREATE = 'create'
DELETE = 'delete'
GET = 'get'
INDEX = 'index'
PATCH = 'patch'
PUT = 'put'

ALL_METHODS = {CREATE, DELETE, GET, INDEX, PATCH, PUT}
INDEX_METHODS = {CREATE, INDEX}
MEMBER_METHODS = {DELETE, GET, PATCH, PUT}

_missing = type('_missing', (), {'__bool__': lambda self: False})()
