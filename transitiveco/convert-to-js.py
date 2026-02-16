#!/usr/bin/env python
# Konvertas la listo de vorto-transitiveco al JS-skripto, por uzi en la retpagxo.

trans = open('transitiveco.txt', 'r')
js = open('transitiveco.js', 'w')

print("// @license magnet:?xt=urn:btih:90dc5c0be029de84e523b9b3922520e79e0e6f08&dn=cc0.txt CC0-1.0", file=js)
print("'use strict';", file=js)

NTR = 0
TR = 1
TR_NTR = 2

print('var transitiveco = {', file=js)

def kurtnomo_al_cifero(s):
    if s == 't':
        return TR
    if s == 'n':
        return NTR
    if s == 'tn':
        return TR_NTR
    raise Exception('nevalida transitiveco: %s' % s)

# Po linio enhavas verbon kaj 't', 'n', aux 'tr', kiu signifas ambaux formojn.
for linio in trans.readlines():
    partoj = linio.strip().split()
    print('%s:%s,' % (partoj[0], kurtnomo_al_cifero(partoj[1])), file=js)

print('};', file=js)

print("function trovu_transitivecon(vorto) {", file=js)
print("    var sercxo = transitiveco[vorto];", file=js)
print("    if (sercxo === undefined)", file=js)
print("        return '';", file=js)
print("    if (sercxo === %s)" % NTR, file=js)
print("        return 'ntr';", file=js)
print("    if (sercxo === %s)" % TR, file=js)
print("        return 'tr';", file=js)
print("    if (sercxo === %s)" % TR_NTR, file=js)
print("        return 'tr/ntr';", file=js)
print("    return '';", file=js)
print("}", file=js)
print("// @license-end", file=js)

trans.close()
js.close()
