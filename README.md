# Minidom Extension

## Short presentation

Functions to improve xml.dom.minidom [1] tools in Python.

class DOMCompanion :
-	def __init__(self, doc = None) : to build a DOM DocumentCompanion
-	def parse(self, file, validate = False): to load an XML file
-	def getElementsByTagName(self, name) : DOM getElementsByTagName
-	def getElementById(self, id) : to retrieve an element by its ID
-   def getAttributsByIdref(self, id) : to retrieve attributs that refers to an ID
-	def toLighter(self, del_spaces = True, del_comments = True, del_pi = True) : to suppress text nodes (with only separators), processing instructions and/or comments
-	def validate(self) : to validate the XML according its DTD (enrich it too)

## Exemple

```
from minidom_ext.DOMCompanion import DOMCompanion

cine = DOMCompanion()
cine.parse("semaine10.xml", True)
print(cine.doc.toxml())
print(cine.getElementById('Ka'))
print(cine.toLighter().toxml())
```


## How to install ?

```
pip install minidom-ext
```


## Links

[1] Python 'minidom' : https://docs.python.org/3/library/xml.dom.minidom.html

[2] DOM using Python : https://docs.python.org/3/library/xml.dom.html

(c) E. Desmontils, University of Nantes, november 2020
