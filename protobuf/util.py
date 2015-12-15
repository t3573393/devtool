# -*- coding: UTF-8 -*-


class ParseException(Exception):

    def __str__(self):
        return 'parse the json error'


def toCamelCase(name, has_title=False):
  """Converts name to camel-case and returns it."""
  capitalize_next = False
  result = []

  for c in name:
    if c == '_':
      if result:
        capitalize_next = True
    elif capitalize_next:
      result.append(c.upper())
      capitalize_next = False
    else:
      result += c

  # Lower-case the first letter.
  if not has_title:
    if result and result[0].isupper():
      result[0] = result[0].lower()
  else:
      result[0] = result[0].title()

  return ''.join(result)


def to_singular(name):
    result = name
    if name.endswith('ies'):
        result = name[:-3] + 'y'
    elif name.endswith('oes'):
        result = name[:-2]
    elif name.endswith('s'):
        result = name[:-1]
    return ''.join(result)

def to_message_name(name):
    return to_singular(toCamelCase(name, has_title=True))