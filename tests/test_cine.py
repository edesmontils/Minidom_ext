#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from minidom_ext.DOMCompanion import DOMCompanion

cine = DOMCompanion()
cine.parse("semaine10.xml", True)
print(cine.doc.toxml())
print(cine.getElementById('Ka'))
print(cine.toLighter().toxml())
print(cine.getAttributsByIdref('Ka'))