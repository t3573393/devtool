# -*- coding: UTF-8 -*-
import json
import logging
from const import *
from util import ParseException, to_message_name


def _decide_scalar_type(value):
    if isinstance(value, basestring):
        return TYPE_STRING
    elif isinstance(value, float):
        return TYPE_DOUBLE
    elif isinstance(value, int):
        return TYPE_INT32
    elif isinstance(value, long):
        return TYPE_INT64
    elif value is None:
        return TYPE_STRING
    return MAX_TYPE


def _decide_base_type(value, for_list=False):
    list_match_dict = {
        int: TYPE_BASE_INT_LIST,
        long: TYPE_BASE_INT_LIST,
        basestring: TYPE_BASE_STRING_LIST,
        float: TYPE_BASE_DOUBLE_LIST,
    }

    dict_match_dict = {
        (int, int): TYPE_BASE_INT_MAP,
        (int, long): TYPE_BASE_INT_MAP,
        (int, basestring): TYPE_BASE_INT_STRING_MAP,
        (int, float): TYPE_BASE_INT_DOUBLE_MAP,
        (basestring, int): TYPE_BASE_STRING_INT_MAP,
        (basestring, long): TYPE_BASE_STRING_INT_MAP,
        (basestring, basestring): TYPE_BASE_STRING_MAP,
        (basestring, float): TYPE_BASE_STRING_DOUBLE_MAP
    }
    # only support [[v,v]] format in list
    if isinstance(value, list) or isinstance(value, tuple):
        if _is_same_type(value):
            first_value = value[0]
            for key, value in list_match_dict.items():
                if isinstance(first_value, key):
                    return value
    elif isinstance(value, dict) and not for_list:
        if _is_same_type(value.keys()) and _is_same_type(value.values()):
            key, value = value.items()[0]
            for a_key, a_value in dict_match_dict.items():
                if isinstance(key, a_key[0]) and isinstance(value, a_key[1]):
                    return a_value
    return MAX_TYPE


def _is_same_type(value):
    is_all_same_type = True
    original_type = None
    for i in value:
        if original_type is None:
            original_type = type(i)
        elif original_type != type(i):
            is_all_same_type = False
            break
    return is_all_same_type


def _decide_label_and_type(name, value):
    scalar_type = _decide_scalar_type(value)
    if scalar_type != MAX_TYPE:
        return LABEL_OPTIONAL, scalar_type
    elif isinstance(value, list):
        return LABEL_REPEATED, _decide_list_type(name, value)
    elif isinstance(value, dict):
        dict_type = _decide_dict_type(name, value)
        if dict_type == TYPE_MESSAGE:
            return LABEL_OPTIONAL, dict_type
        return LABEL_REPEATED, dict_type
    return MAX_LABEL, MAX_TYPE


def _decide_list_type(name, value):
    if len(value) == 0:
        logging.warning('key %s list is empty, use default int32' % name)
        return TYPE_INT32

    is_all_same_type = True
    original_type = None
    for i in value:
        if original_type is None:
            original_type = type(i)
        elif original_type != type(i):
            is_all_same_type = False
            break

    if is_all_same_type:
        i = value[0]
        scalar_type = _decide_scalar_type(i)
        if scalar_type != MAX_TYPE:
            return scalar_type

        base_type = _decide_base_type(i, for_list=True)
        if base_type != MAX_TYPE:
            return base_type

        # special type
        if isinstance(i, list):
            return TYPE_LIST_LIST
        elif isinstance(i, dict):
            return TYPE_LIST_DICT
    else:
        logging.error('key %s list is not the same type' % name)
        raise ParseException('key %s : list type decide error' % name)

    return MAX_TYPE


def _decide_dict_type(name, value):
    if len(value) == 0:
        logging.warning('key %s dict is empty, use default int32' % name)
        return TYPE_BASE_INT_MAP

    is_all_same_type = True
    original_type = None
    for i in value.values():
        if original_type is None:
            original_type = type(i)
        elif original_type != type(i):
            is_all_same_type = False
            break

    if is_all_same_type:
        base_type = _decide_base_type(value)
        if base_type != MAX_TYPE:
            return base_type

        i = value.values()[0]
        # special type
        if isinstance(i, list):
            return TYPE_DICT_LIST
        elif isinstance(i, dict):
            return TYPE_DICT_DICT
    else:
        return TYPE_MESSAGE

# name: proto_dict
global_proto_pool = dict()


def get_new_name(name, alias_pool):
    if alias_pool and name in alias_pool:
        return alias_pool[name]
    return name


def get_proto_file_des(name, json_str, alias_pool=None, custom_prefix=''):
    global global_proto_pool
    # field_name:{'label': label, 'field_type':type, 'flag': flag, 'ext': ext_info, 'custom_type': custom_type}
    proto_dict = dict()
    if isinstance(json_str, dict):
        json_dict = json_str
    else:
        json_dict = json.loads(json_str)

    for key, value in json_dict.items():
        label, field_type = _decide_label_and_type(key, value)
        new_key = get_new_name(key, alias_pool)
        # convert the list dict
        if field_type == TYPE_LIST_DICT:
            custom_name = to_message_name(new_key)
            proto_dict[new_key] = {
                BASE_LABEL: label,
                BASE_FIELD_TYPE: TYPE_MESSAGE,
                BASE_FLAG: FLAG_CUSTOM,
                BASE_EXT: value[0],
                BASE_CUSTOM_TYPE: custom_prefix + get_new_name(custom_name, alias_pool)
            }
        elif field_type == TYPE_DICT_DICT:
            custom_name = to_message_name(new_key)
            proto_dict[new_key] = {
                BASE_LABEL: LABEL_OPTIONAL,
                BASE_FIELD_TYPE: TYPE_MESSAGE,
                BASE_FLAG: FLAG_CUSTOM,
                BASE_EXT: value,
                BASE_CUSTOM_TYPE: custom_prefix + get_new_name(custom_name, alias_pool)
            }
        elif field_type == TYPE_DICT_LIST:
            custom_name = to_message_name(new_key)
            proto_dict[new_key] = {
                BASE_LABEL: LABEL_OPTIONAL,
                BASE_FIELD_TYPE: TYPE_MESSAGE,
                BASE_FLAG: FLAG_CUSTOM,
                BASE_EXT: value,
                BASE_CUSTOM_TYPE: custom_prefix + get_new_name(custom_name, alias_pool)
            }
        elif field_type == TYPE_MESSAGE:
            custom_name = to_message_name(new_key)
            proto_dict[new_key] = {
                BASE_LABEL: label,
                BASE_FIELD_TYPE: TYPE_MESSAGE,
                BASE_FLAG: FLAG_CUSTOM,
                BASE_EXT: value,
                BASE_CUSTOM_TYPE: custom_prefix + get_new_name(custom_name, alias_pool)
            }
        else:
            proto_dict[new_key] = {
                BASE_LABEL: label,
                BASE_FIELD_TYPE: field_type,
                BASE_FLAG:_get_flag(field_type),
                BASE_EXT: value
            }

    new_name = get_new_name(name, alias_pool)
    global_proto_pool[new_name] = proto_dict

    # handle the submessage
    for field_name, field_value in proto_dict.items():
        if field_value[BASE_FIELD_TYPE] == TYPE_MESSAGE:
            get_proto_file_des(field_value[BASE_CUSTOM_TYPE], field_value[BASE_EXT], custom_prefix=custom_prefix)


def _get_label_str(label_value):
    match_dict = {
        LABEL_OPTIONAL : 'optional',
        LABEL_REPEATED: 'repeated',
        LABEL_REQUIRED: 'required'
    }
    return match_dict[label_value]


def _get_type_str(type_value):
    match_dict = {
        TYPE_DOUBLE : 'double',
        TYPE_FLOAT: 'float',
        TYPE_UINT64: 'uint64',
        TYPE_INT64 : 'int64',
        TYPE_INT32: 'int32',
        TYPE_FIXED64: 'fixed64' ,
        TYPE_FIXED32 : 'fixed32',
        TYPE_BOOL: 'bool',
        TYPE_STRING: 'string',
        TYPE_BYTES: 'bytes' ,
        TYPE_UINT32 : 'uint32',
        TYPE_SFIXED32: 'sfixed32',
        TYPE_SFIXED64 : 'sfixed64',
        TYPE_SINT32: 'sint32',
        TYPE_SINT64: 'sint64',
        TYPE_BASE_INT_MAP: 'IntMapFieldEntry',
        TYPE_BASE_INT_STRING_MAP: 'IntStringMapFieldEntry',
        TYPE_BASE_INT_DOUBLE_MAP: 'IntDoubleMapFieldEntry',
        TYPE_BASE_STRING_MAP: 'StringMapFieldEntry',
        TYPE_BASE_STRING_INT_MAP: 'StringIntFieldEntry',
        TYPE_BASE_STRING_DOUBLE_MAP: 'StringDoubleFieldEntry',
        TYPE_BASE_INT_LIST: 'IntListFieldEntry',
        TYPE_BASE_STRING_LIST: 'StringListFieldEntry',
        TYPE_BASE_DOUBLE_LIST: 'DoubleListFieldEntry',
    }
    return match_dict[type_value]


def generate_proto_file(package_name, no_base=False):
    global global_proto_pool
    content = 'package\t%s;\n' % package_name

    if not no_base:
        content += BaseProtoString
    else:
        content += '\n'

    names = global_proto_pool.keys()
    names.sort()
    for name in names:
        index = 1

        field_objs = global_proto_pool[name]
        content += "message %s {\n" % name
        for a_field_name, a_field in field_objs.items():
            extra_str = ''
            label = a_field[BASE_LABEL]
            field_type = a_field[BASE_FIELD_TYPE]
            if field_type not in [TYPE_LIST_LIST, TYPE_LIST_DICT, TYPE_DICT_LIST, TYPE_DICT_DICT, TYPE_MESSAGE]:
                if field_type in [TYPE_DOUBLE, TYPE_FLOAT, TYPE_INT64, TYPE_UINT64, TYPE_INT32,
                                  TYPE_UINT32, TYPE_SINT32, TYPE_SINT64] and label == LABEL_REPEATED:
                    extra_str = '[packed=true]'

                content += "    %s %s %s = %s %s;\n" % (_get_label_str(label), _get_type_str(field_type),
                                                        a_field_name,  index, extra_str)
            elif field_type == TYPE_MESSAGE:
                content += "    %s %s %s = %s %s;\n" % (_get_label_str(label), a_field[BASE_CUSTOM_TYPE],
                                                        a_field_name,  index, extra_str)
            else:
                content += "    %s unknown_type %s =%s;\t#%s\n" % (_get_label_str(LABEL_OPTIONAL),
                                                                   a_field_name,  index, a_field[BASE_EXT])
                logging.error('message %s field :%s no generate %s-%s' % (name, a_field_name, label, field_type))
            index += 1
        content += "}\n"
        content += "\n"
    return content


def generate(package_name, root_message_name, json_str, target_file='result.proto', alias_pool=None, custom_prefix='',no_base=False):
    """
    入口函数
    :param package_name: 包名称
    :param root_message_name:  根消息名称
    :param json_str:  需要解析的 json
    :param target_file:  目标文件路径
    :param alias_pool: 别名列表
    :param custom_prefix: 自定义前缀
    :param no_base: 是否需要包含base的信息
    :return:
    """

    logging.debug('start ...')
    # generate the des
    get_proto_file_des(root_message_name, json_str, alias_pool=alias_pool, custom_prefix=custom_prefix)

    # generate string by des
    with open(target_file, mode='w') as f:
        f.write(generate_proto_file(package_name, no_base=no_base))

    logging.debug('the end')


def _get_flag(field_type):
    if field_type < 20:
        return FLAG_ORIGINAL
    elif 100 > field_type >= 20:
        return FLAG_USE_BASE
    return FLAG_CUSTOM


if __name__ == "__main__":
    # json_str = """{"string_value": "456", "int_value": 32, "double_value": 6.5, "int_list_empty_value":[],
    # "int_list_value":[3,2], "string_list_value": ["32", "33"], "double_list_value": [9.6,6.5],
    # "int_list_list_value": [[3,32], [32,4,5]], "list_list_value": [[3,[4, 6],3], [32,4,5]],
    # "list_dict_value": [{"32":3}], "empty_dict": {}, "string_int_dict": {"32": 3}, "string_dict": {"323": "fdsafsd"},
    # "string_double_dict": {"fdas":5.6}, "dict_list_dict":{"fdsa":[32,4], "fdsxa":[3,6,7]}, "dict_dict": {"fdsa":{"xx":3}},
    # "string_message": {"fdsafas":32, "xx":"432", "ca": [3,4,5]}
    # }"""

    json_str = """
{"monster_star": 1, "monster_strong": 1.0, "exists_num": [180000], "monster_level": 20, "open_time": null, "boss_monster": "", "reset_time": 1, "map_bg_res": ["battle_014"], "sweeping_times": 2, "map_kind": 4, "map_id": 40101, "boss_strong": 1.0, "monster_quality": 1, "monsters": {}, "enter_state": 1}
    """

    # test parse
    # json_dict = json.loads(json_str)
    # for key, value in json_dict.items():
    #     a_label, a_type = _decide_label_and_type(key, value)
    #     print key, a_label, a_type

    # test generate
    # import pprint
    # get_proto_file_des('linfeng', json_str)
    # p = pprint.PrettyPrinter()
    # p.pprint(global_proto_pool)

    # package name, root message name, json string, alias mapping for message name and field name
    generate('linfengtest', 'FairylandMapTemplate', json_str, alias_pool={
    }, custom_prefix='', no_base=True)







