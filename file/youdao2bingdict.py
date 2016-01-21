import xml.etree.ElementTree as ET
import datetime

"""
use for transform between youdao dict and bing dict
"""
YOUDAO_MAP_TABLE = {
    'word': 'eng',
    'trans': 'defi',
    'phonetic': 'phonetic',
    'tags': 'note'
}


BING_MAP_TABLE = {
    'Eng': 'eng',
    'Defi': 'defi',
    'Phonetic': 'phonetic',
    'Note': 'note'
}


def youdao2bing(src_file_name, target_file_name):
    word_list = list()
    tree = ET.parse(src_file_name)
    root = tree.getroot()
    for child in root:
        w = dict()
        for key, target_key in YOUDAO_MAP_TABLE.items():
            value = child.find(key).text
            w[target_key] = value
        word_list.append(w)

    root_element = ET.Element('FCVocaPhraseList', {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
    })

    now_time = datetime.datetime.now()
    phrases_element = ET.SubElement(root_element, 'Phrases')
    for a_word in word_list:
        phrase_element = ET.SubElement(phrases_element, 'Phrase')

        date_element = ET.SubElement(phrase_element, 'Date')
        date_element.text = now_time.strftime('%Y-%m-%d %H:%M:%S')
        for src_key, target_key in BING_MAP_TABLE.items():
            src_element = ET.SubElement(phrase_element, src_key)
            src_element.text = a_word[target_key]
    target_tree = ET.ElementTree(root_element)
    target_tree.write(target_file_name, encoding="utf-8", xml_declaration=True)


def bing2youdao(src_file_name, target_file_name):
    word_list = list()
    tree = ET.parse(src_file_name)
    root = tree.getroot().find('Phrases')
    for child in root:
        w = dict()
        for key, target_key in BING_MAP_TABLE.items():
            value = child.find(key).text
            w[target_key] = value
        word_list.append(w)

    root_element = ET.Element('wordbook')
    for a_word in word_list:
        item_element = ET.SubElement(root_element, 'item')

        src_element = ET.SubElement(item_element, 'progress')
        src_element.text = '0'
        for src_key, target_key in YOUDAO_MAP_TABLE.items():
            src_element = ET.SubElement(item_element, src_key)
            src_element.text = a_word[target_key]
    target_tree = ET.ElementTree(root_element)
    target_tree.write(target_file_name, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    youdao2bing('1.xml', '2.xml')
    bing2youdao('3.xml', '4.xml')