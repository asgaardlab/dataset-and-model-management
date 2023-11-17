from enum import Enum


class CallRootType(Enum):
    IMPORT = 'import'
    TYPE_IMPORT = 'type_import'
    CUSTOM_FUNCTION = 'custom_function'
    TYPE_METHOD = 'type_method'
    FUNCTION_PARAMETER = 'function_parameter'
    CONSTANT = 'constant'
    UNKNOWN = 'unknown'
    ASSIGNMENT = 'assignment'
    ASSIGNMENT_CLASS = 'assignment_class'
    ASSIGNMENT_IMPORT = 'assignment_import'
    ASSIGNMENT_UNKNOWN = 'assignment_unknown'
