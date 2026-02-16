#!/usr/bin/env python
# Converts Paul Denisowski's ESPDIC project to JS array format.
# The resulting file shares the same license as ESPDIC: CC-BY-3.0.

import re

espdic = open('espdic.txt', 'r')
js = open('espdic.js', 'w')
print('// @license magnet:?xt=urn:btih:8c49db20840818d3c29cb43b48f608e20a456abc&dn=cc-by-3.0.txt CC-BY-3.0', file=js)
print('// ESPDIC by Paul Denisowski.', file=js)
print("'use strict';", file=js)
print('var espdic = [', file=js)

# The first line is authorship information.
espdic.readline()

# Each line thereafter contains something like a word and a definition.
# The two parts are always separated by " : ".
for line in espdic.readlines():
    line = line.replace('"', '\\"')

    esperanto, english = line.strip().split(' : ')

    # The English translations offer multiple suggestions.
    # For searching in English, we can break these up.
    # Split after a comma-space or semicolon-space.
    engarray = re.split(', |; ', english)

    print('["%s","%s"],' % (esperanto, '","'.join(engarray)), file=js)

print('];', file=js)

# Construct a lowercase version of espdic.
# Done on load since it's very fast, even on phones.
# Chrome seems to not like a.map(String.prototype.toLowerCase).
print('var espdic_lower = espdic.map(function(a) { return a.map(function(x) { return x.toLowerCase(); }) });', file=js)
print('// @license-end', file=js)

espdic.close()
js.close()
