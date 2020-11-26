#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
	Functions to improve xml.dom.minidom tools in Python.
"""
import os
from xml.dom.minidom import Node, Element, parse
import re
from lxml import etree  # http://lxml.de/index.html#documentation

#==================================================
#============ Tools ===============================
#==================================================

def existFile(f):
	""" tests if the file exists """
	return os.path.isfile(f)

def existDir(d):
	""" tests if the directory exists """
	return os.path.exists(d)

#==================================================
#============ class DOMCompanion ==================
#==================================================

class DOMCompanion :
	"""
		Functions to improve xml.dom.minidom tools in Python.

		Attributes
		----------
		doc : Node.DOCUMENT_NODE
			the DOM structure
		documentElement : Node.ElEMENT_NODE
			equivalent to doc.documentElement
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
		self.lid = dict()
		if doc is not None :
			self.documentElement = doc.documentElement
			self.enrichXML()
		else :
			self.documentElement = None

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

			See Also
			--------
			`DOMCompanion.validate`
			`DOMCompanion.enrichXML`

			Notes
			-----
			if a DTD is specified, uses it to add default attributes and to collect IDs
		"""
		if existFile(file) :
			self.doc = parse(file)
			self.documentElement = self.doc.documentElement
			if validate :
				self.validate()
			else :
				self.enrichXML()

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

			See Also
			--------
			`DOMCompanion.purgeDOM`
		"""
		if self.doc is not None :
			self.purgeDOM(self.doc, del_spaces, del_comments, del_pi)
		return self

	# ===========================================================================================
	def validate(self) :
		"""
			to validate the XML according its DTD (enrich it too). It uses lxml module to validate the XML document.

			Returns
			-------
			boolean
				the DOM is valid or not according to the specified DTD

			See Also
			--------
			`DOMCompanion.enrichXML`
		"""
		if self.doc is not None :
			parser = etree.XMLParser(recover=True, strip_cdata=True)
			tree = etree.XML(self.doc.toxml(), parser)
			dtdFile = self.doc.doctype.systemId
			if dtdFile is not None :
				if existFile(dtdFile) :
					dtd = etree.DTD(dtdFile)
					if dtd.validate(tree) :
						self.enrichXML()
						return True
					else :
						print(dtd.error_log.filter_from_errors()[0])
						return False
				else :
					print('Unable ti find the DTD file ',dtdFile)
					return False
			else:
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
		"""
		return self.doc.toxml()

	# ===========================================================================================
	#####################################
	########## private methods ##########
	#####################################

	def enrichXML(self) :
		if self.doc is not None :
			self.lid = dict()
			dtdFile = self.doc.doctype.systemId
			if dtdFile is not None :
				if existFile(dtdFile) :
					le = self.extractDTD(dtdFile)
					self.enrichNode(self.doc.documentElement, le)
				else :
					print('Unable ti find the DTD file ',dtdFile)

	def purgeDOM(self, no, del_spaces, del_comments, del_pi) :
		if no.nodeType in [Node.ELEMENT_NODE, Node.DOCUMENT_NODE] :
			toDel = []
			for n in no.childNodes :
				if del_spaces and n.nodeType == Node.TEXT_NODE and n.data.strip('\t \n') == '' :
					toDel.append(n)
				elif del_comments and n.nodeType == Node.COMMENT_NODE :
					toDel.append(n)
				elif del_pi and n.nodeType == Node.PROCESSING_INSTRUCTION_NODE :
					toDel.append(n)
				elif n.nodeType == Node.ELEMENT_NODE :
					self.purgeDOM(n,del_spaces,del_comments, del_pi)
			for n in toDel :
				no.removeChild(n)
		elif no.nodeType == Node.DOCUMENT_TYPE_NODE :
			pass
		else :
			pass
		return no


	def getDTD(self, file) :
		if existFile(file) :
			f = open(file,'r')
			dtd = f.read()
			f.close()
			return dtd
		else :
			return None


	def extractDTD(self, file) :

		el = re.compile(r'<!ELEMENT (?P<elementname>[\w\-\:\_]+) (?P<description>.*)\s*>')
		att = re.compile(r'<!ATTLIST (?P<elementname>[\w\-\:\_]+) (?P<attributs>.*)\s*>')
		att2 = re.compile(r'(?P<attname>[\w\-\:\_]+) (?P<def>.*?) (?P<status>#[\w\-\:\_]+|[\"\'].*?[\"\'])')
		comment = re.compile(r'<!-- \.*? -->')

		dtd = self.getDTD(file).replace('\n',' ').replace('\t',' ')
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


	def enrichNode(self, node, le) :
		if node.nodeType == Node.ELEMENT_NODE :
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
			for n in node.childNodes :
				self.enrichNode(n,le)


if ( __name__ == "__main__"):
	cine = DOMCompanion()
	cine.parse("semaine10.xml", True)
	print(cine.doc.toxml())
	print(cine.getElementById('Ka'))
	print(cine.toLighter().toxml())