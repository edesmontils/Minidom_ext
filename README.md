# Minidom Extension

## Short presentation

Functions to improve xml.dom.minidom tools in Python.
class DOMDocumentCompanion :
-	def __init__(self, doc = None) : build a DOM DocumentCompanion
-	def parse(self, file, validate = False): load en XML file
-	def enrichXML(self) : adds default attribute and detects IDs
-	def getElementsByTagName(self, name) : DOM getElementsByTagName
-	def getElementById(self, id) : retrieve an element by its ID (only if "enrichXML" or "validate" is done)
-	def toLighter(self, del_spaces = True, del_comments = True, del_pi = True) : to suppress text nodes (with only separators), processing instructions and/or comments
-	def validate(self) : validate the XML according its DTD (enrich it too)

## Exemple

```
cine = DOMDocumentCompanion()
cine.parse("semaine10.xml", True)
print(cine.doc.toxml())
print(cine.getElementById('Ka'))
print(cine.toLighter().toxml())
```


## Links

[1] Python 'minidom' : https://docs.python.org/3/library/xml.dom.minidom.html


(c) E. Desmontils, University of Nantes, november 2020