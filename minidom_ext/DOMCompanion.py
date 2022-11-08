#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
	Functions to improve xml.dom.minidom tools in Python.
"""
import os
from xml.dom.minidom import Node, Element, parse, parseString
import re
from lxml import etree  # http://lxml.de/index.html#documentation
import xpath #https://github.com/jackjansen/py-dom-xpath-six


# pdoc3 --html --force minidom_ext.py

#==================================================
#============ Tools ===============================
#==================================================

def _existFile(f):
	""" tests if the file exists """
	return os.path.isfile(f)

def _existDir(d):
	""" tests if the directory exists """
	return os.path.exists(d)

#==================================================
#============ class DOMCompanion ==================
#==================================================

class DOMCompanion :
	"""
		Functions to improve xml.dom.minidom tools in Python.
	"""

	# ===========================================================================================
	def __init__(self, doc = None) :
		"""
			class constructor.

			Parameters
			----------
			doc : Node.DOCUMENT_NODE, optional
				DOM structure

			Notes
			-----
			The DOM is also enriched with default attributes if a DTD is specified
		"""
		self.doc = doc
		"""
			the DOM structure : Node.DOCUMENT_NODE
		"""
		self.documentElement = None
		"""
			equivalent to doc.documentElement : Node.ELEMENT_NODE
		"""
		self.lid = dict()
		if doc is not None :
			self.documentElement = doc.documentElement
			self._enrichXML()
			

	# ===========================================================================================
	def parse(self, file, validate = False):
		""" 
			to load an XML file

			Parameters
			----------
			file : str
				file that contains the XML file to load

			validate : boolean, optional
				flag to validate the XML file if it contains a Doctype section

			Returns
			-------
			boolean
				the DOM is valid or not according to the specified DTD
				True if there is no DTD

			See Also
			--------
			`DOMCompanion.validate`

			Notes
			-----
			if a DTD is specified, uses it to add default attributes and to collect IDs
			See https://docs.python.org/3/library/xml.dom.minidom.html
		"""
		if _existFile(file) :
			self.doc = parse(file)
			self.documentElement = self.doc.documentElement
			if validate :
				if self.validate() :
					return True
				else :
					self._enrichXML()
					return False
			else :
				self._enrichXML()
				return True

	# ===========================================================================================
	def parseString(self, xml, validate = False):
		""" 
			to load an XML string

			Parameters
			----------
			xml : str
				the string that contains the XML

			validate : boolean, optional
				flag to validate the XML file if it contains a Doctype section

			Returns
			-------
			boolean
				the DOM is valid or not according to the specified DTD
				True if there is no DTD

			See Also
			--------
			`DOMCompanion.validate`

			Notes
			-----
			if a DTD is specified, uses it to add default attributes and to collect IDs
			See https://docs.python.org/3/library/xml.dom.minidom.html
		"""
		self.doc = parseString(xml)
		self.documentElement = self.doc.documentElement
		if validate :
			if self.validate() :
				return True
			else :
				self._enrichXML()
				return False
		else :
			self._enrichXML()
			return True

	# ===========================================================================================
	def xpath(self, xp) :
		"""
			search XML with XPath

			Parameters
			----------
			name : xp
				the XPath expression to search in the DOM

			Returns
			-------
			nodeList
				nodes finded by xp

			Notes
			-----
			See https://docs.python.org/3/library/xml.dom.minidom.html
			    https://github.com/jackjansen/py-dom-xpath-six
		"""
		return xpath.find(xp, self.doc)


	# ===========================================================================================
	def getElementsByTagName(self, name) :
		"""
			the DOM getElementsByTagName

			Parameters
			----------
			name : str
				the Element to find in the DOM

			Returns
			-------
			NodeList or None
				a list of elements or None
		"""
		if self.doc is not None :
			return self.doc.getElementsByTagName(name)
		else:
			return None

	# ===========================================================================================
	def getElementById(self, id) :
		"""
			to retrieve an element by its ID
			
			Parameters
			----------
			id : str
				the ID of the element to find

			Returns
			-------
			Node.ELEMENT_NODE or None
				the element or None
		"""
		if id in self.lid.keys() :
			return self.lid[id]
		else :
			return None

	# ===========================================================================================
	def getAttributsByIdref(self, id) :
		"""
			to retrieve IDREF attributs with an ID
			
			Parameters
			----------
			id : str
				the ID to looking for

			Returns
			-------
			List(Attr)
				the attributs
		"""
		# if id in self.lid.keys() :
		# 	return self.lid[id]
		# else :
		return self._getIdrefs(self.doc.documentElement, id)



	# ===========================================================================================
	def toLighter(self, del_spaces = True, del_comments = True, del_pi = True) :
		"""
			to suppress text nodes (with only separators), processing instructions and/or comments

			Parameters
			----------
			del_spaces : boolean, optional
				to suppress blank nodes (with only newline, tabulation et space caracters)
			del_comments : boolean, optional
				to suppress comment nodes
			del_spaces : boolean, optional
				to suppress processing instruction nodes

			Returns
			-------
			DOMCompaniom
				itself
		"""
		if self.doc is not None :
			self._purgeDOM(self.doc, del_spaces, del_comments, del_pi)
		return self

	# ===========================================================================================

	def validate(self) :
		"""
			to validate the XML according its DTD (enrich it too). It uses lxml module to validate the XML document.

			Returns
			-------
			boolean
				the DOM is valid or not according to the specified DTD
		"""
		if self.doc is not None :
			parser = etree.XMLParser(recover=True, strip_cdata=True)
			tree = etree.XML(self.doc.toxml(), parser)
			dtdFile = self._getDTDFile()
			if dtdFile is not None :
				if _existFile(dtdFile) :
					dtd = etree.DTD(dtdFile)
					if dtd.validate(tree) :
						self._enrichXML()
						return True
					else :
						print(dtd.error_log.filter_from_errors()[0])
						return False
				else :
					print('Unable to find the DTD file ',dtdFile)
					return False
			else:
				self._enrichXML()
				return True
		else :
			return False

	# ===========================================================================================
	def toxml(self) :
		"""
			produce XML string

			Returns
			-------
			str
				the XML string

			Notes
			-----
			See https://docs.python.org/3/library/xml.dom.minidom.html
		"""
		return self.doc.toxml()

	# ===========================================================================================
	def toprettyxml(self,indent="\t", newl="\n", encoding=None, standalone=None) :
		"""
			produce pretty-printed version of the XML string

			Returns
			-------
			str
				the XML string

			Notes
			-----
			See https://docs.python.org/3/library/xml.dom.minidom.html
		"""
		return self.doc.toprettyxml(ident, newl, encoding, standalone)

	# ===========================================================================================
	#####################################
	########## private methods ##########
	#####################################

	def _getDTDFile(self) :
		if self.doc.doctype is not None :
			if self.doc.doctype.systemId is not None :
				return self.doc.doctype.systemId
			else : return None
		else : return None


	def _enrichXML(self) :
		if self.doc is not None :
			self.lid = dict()
			dtdFile = self._getDTDFile()
			if dtdFile is not None :
				if _existFile(dtdFile) :
					le = self._extractDTD(dtdFile)
					self._enrichNode(self.doc.documentElement, le)
				else :
					print('Unable ti find the DTD file ',dtdFile)
			else :
				self._enrichNode(self.doc.documentElement, dict())
		else : self._enrichNode(self.doc.documentElement, dict())

	def _purgeDOM(self, no, del_spaces, del_comments, del_pi) :
		# if no.nodeType in [Node.ELEMENT_NODE, Node.DOCUMENT_NODE] :
		# 	toDel = []
		# 	for n in no.childNodes :
		# 		if del_spaces and n.nodeType == Node.TEXT_NODE and n.data.strip('\t \n') == '' :
		# 			toDel.append(n)
		# 		elif del_comments and n.nodeType == Node.COMMENT_NODE :
		# 			toDel.append(n)
		# 		elif del_pi and n.nodeType == Node.PROCESSING_INSTRUCTION_NODE :
		# 			toDel.append(n)
		# 		elif n.nodeType == Node.ELEMENT_NODE :
		# 			self._purgeDOM(n,del_spaces,del_comments, del_pi)
		# 	for n in toDel :
		# 		no.removeChild(n)
		# elif no.nodeType == Node.DOCUMENT_TYPE_NODE :
		# 	pass
		# else :
		# 	pass
		# return no
		if (no.nodeType in [Node.ELEMENT_NODE, Node.DOCUMENT_NODE]) and (no.hasChildNodes()) :
			n = no.firstChild
			while (isinstance(n,Node)) :
				toDel = (del_spaces and n.nodeType == Node.TEXT_NODE and n.data.strip('\t \n') == '') \
				     or (del_comments and n.nodeType == Node.COMMENT_NODE) \
				     or (del_pi and n.nodeType == Node.PROCESSING_INSTRUCTION_NODE)
				nextN = n.nextSibling
				if toDel : 
					no.removeChild(n)
				elif n.nodeType == Node.ELEMENT_NODE : 
					self._purgeDOM(n,del_spaces,del_comments, del_pi)
				n = nextN
		return no

	def _getIdrefs(self, no, value) :
		idrefAttributes = list()
		if no.nodeType == Node.ELEMENT_NODE :
			latt = no.attributes
			for i in range(latt.length) :
				att = latt.item(i)
				if att.value == value :
					if self.lid[att.value] != no :
						idrefAttributes.append(att)
			for n in no.childNodes :
				if n.nodeType == Node.ELEMENT_NODE :
					idrefAttributes += self._getIdrefs(n,value)
		else :
			pass
		return idrefAttributes


	def _getDTD(self, file) :
		if _existFile(file) :
			f = open(file,'r')
			dtd = f.read()
			f.close()
			return dtd
		else :
			return None


	def _extractDTD(self, file) :

		el = re.compile(r'<!ELEMENT (?P<elementname>[\w\-\:\_]+) (?P<description>.*)\s*>')
		att = re.compile(r'<!ATTLIST (?P<elementname>[\w\-\:\_]+) (?P<attributs>.*)\s*>')
		att2 = re.compile(r'(?P<attname>[\w\-\:\_]+) (?P<def>.*?) (?P<status>#[\w\-\:\_]+|[\"\'].*?[\"\'])')
		comment = re.compile(r'<!-- \.*? -->')

		dtd = self._getDTD(file).replace('\n',' ').replace('\t',' ')
		cp = re.compile(r'<.*?>')
		liste_elem = dict()
		for item in cp.findall(dtd) :
			cmnt = comment.match(item)
			if cmnt is not None :
				pass
			else :
				grp = el.match(item)
				if grp is not None :
					nomElem = grp.group('elementname').strip('\t \n')
					liste_elem[nomElem] = dict()
				else :
					grp = att.match(item)
					if grp is not None :
						nomElem = grp.group('elementname')
						for (nom, definition, status) in att2.findall(grp.group('attributs')) :
							nomAtt = nom.strip('\t \n')
							definition = definition.strip('\t \n')
							status = status.strip('\t \n')
							liste_elem[nomElem][nomAtt] = (definition, status.replace("'",'').replace('"',''))
		return liste_elem


	def _enrichNode(self, node, le) :
		if node.nodeType == Node.ELEMENT_NODE :
			if node.tagName in le :
				la = le[node.tagName]
				for (att, (definition, status)) in la.items() :
					if definition == 'ID' :
						nid = node.getAttribute(att)
						self.lid[nid] = node
					if node.hasAttribute(att) :
						pass
					else :
						if '#' not in status :
							node.setAttribute(att,status)		
			latt = node.attributes
			for i in range(latt.length) :
				att = latt.item(i)
				if att.name.upper() == 'XML:ID' and att.value not in self.lid :
					self.lid[att.value] = node
			for n in node.childNodes :
				self._enrichNode(n,le)


if ( __name__ == "__main__"):
	cine = DOMCompanion()
	cine.parse("../tests/semaine10.xml", True)
	print(cine.doc.toxml())
	print(cine.getElementById('Ka'))
	print(cine.toLighter().toxml())
	print(cine.getAttributsByIdref('Ka'))