#!/usr/bin/env python

import re
import os
import xml.etree.ElementTree as ET
from lxml import etree

# There are a ton of entities defined in src/cfg.
# Apparently these have to be loaded manually and shoved into a custom parser.
def get_entities():
    entities = {}

    # Load entities from all DTDs referenced by vokoxml.dtd.
    for dtd_file in ['src/dtd/vokosgn.dtd', 'src/dtd/vokomll.dtd',
                      'src/dtd/vokoenh.dtd', 'src/dtd/vokourl.dtd']:
        with open(dtd_file, 'rb') as f:
            dtd = etree.DTD(f)
            for entity in dtd.iterentities():
                if entity.content is not None:
                    entities[entity.name] = entity.content

    # Seed some default entities.
    entities[u'apos'] = "'"
    entities[u'quot'] = '"'

    # Resolve nested entity references (e.g. '&a_damma;&a_w;').
    def resolve(val):
        return re.sub(r'&(\w+);', lambda m: entities.get(m.group(1), m.group(0)), val)
    for key in entities:
        entities[key] = resolve(entities[key])

    return entities


# Parse an XML file, resolving custom entities by text substitution.
# (In Python 3, XMLParser.entity is read-only.)
def parse_xml(xml_path, entities):
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content)
    # Use regex to replace only complete entity references (avoid partial matches).
    def replace_entity(m):
        return entities.get(m.group(1), m.group(0))
    content = re.sub(r'&(\w+);', replace_entity, content)
    return ET.ElementTree(ET.fromstring(content))


# Given a root and a kap Element, create the full Esperanto word(s).
def kap_to_esperanto(root, kap):
    # <kap><tld/>i</kap>
    tld = kap.find('tld')
    if tld is None:
        # <kap>Pumpilo</kap>
        word = kap.text.strip()
    else:
        word = ((kap.text or '') + root + (kap.find('tld').tail or '')).strip()

    # Handle <var> in the kap, which specifies variants.
    var = kap.find('var')
    if var is not None:
        # Sometimes the comma separating variants is the tail of another tag.
        # <kap><tld/>ilo<fnt>Z</fnt>,
        word = word + ', ' + kap_to_esperanto(root, var.find('kap'))
        word = word.replace(',,', ',')
        word = word.replace('  ', ' ')

    return re.sub(r'\s+', ' ', word)


# Create language text out of a trd translation element.
def trd_to_text(trd):
    return re.sub(r'\s+', ' ', ''.join(trd.itertext()))


def mark_translation(esperanto, lang, translation):
    global dictionary
    if lang not in dictionary:
        dictionary[lang] = {}

    translation = translation.replace('"', '\\"');

    entries = dictionary[lang]
    if esperanto not in entries:
        entries[esperanto] = [translation]
    elif translation not in entries[esperanto]:
        entries[esperanto].append(translation)


def extract_translations(esperanto, root):
    # Translations.
    # Non-group translations:
    for trd in root.findall('trd'):
        translation = trd_to_text(trd)
        mark_translation(esperanto, trd.attrib['lng'], translation)

    # Group translations:
    for trdgrp in root.findall('trdgrp'):
        lng = trdgrp.attrib['lng']
        for trd in trdgrp.findall('trd'):
            translation = trd_to_text(trd)
            mark_translation(esperanto, lng, translation)


#####################################################################


dictionary = {}


def main():
    entities = get_entities()
    xmlfiles = ['src/xml/' + f for f in os.listdir('src/xml') if f[-4:] == '.xml']

    for xml in xmlfiles:
        tree = parse_xml(xml, entities)
        root = tree.getroot().find('art')

        radiko = root.find('kap').find('rad').text

        # Derivatives of the root.
        for drv in root.iter('drv'):
            esperanto = kap_to_esperanto(radiko, drv.find('kap'))

            extract_translations(esperanto, drv)

            # Senses of meaning of the derivative.
            for snc in drv.iter('snc'):
                extract_translations(esperanto, snc)

    # Output the dictionaries.
    for lang, entries in dictionary.items():
        with open('revo-' + lang + '.js', 'w') as js:

            print('// @license magnet:?xt=urn:btih:cf05388f2679ee054f2beb29a391d25f4e673ac3&dn=gpl-2.0.txt GPL-v2', file=js)
            print('// De La Reta Vortaro', file=js)
            print("'use strict';", file=js)
            print('var revo_%s = [' % lang, file=js)

            ordered = sorted(entries.items())
            for entry in ordered:
                eo = entry[0].replace('"', "'");
                tra = '","'.join(entry[1])
                print('["%s","%s"],' % (eo, tra), file=js)

            print('];', file=js)

            # Construct a lowercase version of the dictionary.
            # Done on load since it's very fast, even on phones.
            print('var revo_%s_lower = revo_%s.map(function(a) { return a.map(function(x) { return x.toLowerCase(); }) });' % (lang, lang), file=js)
            print('// @license-end', file=js)

if __name__ == '__main__':
    main()
