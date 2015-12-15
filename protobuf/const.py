# -*- coding: UTF-8 -*-


# field type
TYPE_DOUBLE         = 1
TYPE_FLOAT          = 2
TYPE_INT64          = 3
TYPE_UINT64         = 4
TYPE_INT32          = 5
TYPE_FIXED64        = 6
TYPE_FIXED32        = 7
TYPE_BOOL           = 8
TYPE_STRING         = 9
TYPE_GROUP          = 10
TYPE_MESSAGE        = 11
TYPE_BYTES          = 12
TYPE_UINT32         = 13
TYPE_ENUM           = 14
TYPE_SFIXED32       = 15
TYPE_SFIXED64       = 16
TYPE_SINT32         = 17
TYPE_SINT64         = 18
MAX_TYPE            = 1000

# base type
TYPE_BASE_INT_MAP = 20
TYPE_BASE_INT_STRING_MAP = 21
TYPE_BASE_INT_DOUBLE_MAP = 22
TYPE_BASE_STRING_MAP = 23
TYPE_BASE_STRING_INT_MAP = 24
TYPE_BASE_STRING_DOUBLE_MAP = 25
TYPE_BASE_INT_LIST = 26
TYPE_BASE_STRING_LIST = 27
TYPE_BASE_DOUBLE_LIST = 28

# special type
TYPE_LIST_LIST = 100
TYPE_LIST_DICT = 101
TYPE_DICT_LIST = 102
TYPE_DICT_DICT = 103

# label
LABEL_OPTIONAL      = 1
LABEL_REQUIRED      = 2
LABEL_REPEATED      = 3
MAX_LABEL           = 100

# base key

BASE_KEY = 'key'
BASE_VALUE = 'value'
BASE_LABEL = 'label'
BASE_FIELD_TYPE = 'field_type'
BASE_FLAG = 'flag'
BASE_EXT = 'ext'
BASE_CUSTOM_TYPE = 'custom_type'

BaseProtoString = """
message IntListFieldEntry {
  repeated int32 value = 1;
}

message StringListFieldEntry {
  repeated string value = 1;
}

message DoubleListFieldEntry {
  repeated double value = 1;
}

message IntMapFieldEntry {
  optional int32 key = 1;
  optional int32 value = 2;
}

message IntStringMapFieldEntry {
    optional int32 key = 1;
    optional string value = 2;
}

message IntDoubleMapFieldEntry {
    optional int32 key = 1;
    optional double value = 2;
}

message StringMapFieldEntry {
    optional string key = 1;
    optional string value = 2;
}

message StringIntFieldEntry {
    optional string key = 1;
    optional int32 value = 2;
}

message StringDoubleFieldEntry {
    optional string key = 1;
    optional double value = 2;
}

"""

FLAG_ORIGINAL = 1
FLAG_USE_BASE = 2
FLAG_CUSTOM = 3


# char

CH = ' '
