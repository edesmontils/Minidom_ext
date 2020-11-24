#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from xml.dom.minidom import Node, Element, parse
import re
from lxml import etree  # http://lxml.de/index.html#documentation

class DOMDocumentCompanion :
	def __init__(self, doc = None) :
		self.doc = doc
		self.lid = dict()
		if doc is not None :
			self.enrichXML()

	def parse(self, file, validate = False):
		self.doc = parse(file)
		if validate :
			self.validate()
		else :
			self.enrichXML()

	def enrichXML(self) :
		self.lid = dict()
		dtdFile = self.doc.doctype.systemId
		if dtdFile is not None :
			le = self.extractDTD(dtdFile)
			self.enrichNode(self.doc.documentElement, le)

	def getElementsByTagName(self, name) :
		return self.doc.getElementsByTagName(name)

	def getElementById(self, id) :
		if id in self.lid.keys() :
			return self.lid[id]
		else :
			return None

	def toLighter(self, del_spaces = True, del_comments = True, del_pi = True) :
		return self.purgeDOM(self.doc, del_spaces, del_comments, del_pi)

	def validate(self) :
		parser = etree.XMLParser(recover=True, strip_cdata=True)
		tree = etree.XML(self.doc.toxml(), parser)
		dtdFile = self.doc.doctype.systemId
		if dtdFile is not None :
			dtd = etree.DTD(dtdFile)
			if dtd.validate(tree) :
				self.enrichXML()
				return True
			else :
				print(dtd.error_log.filter_from_errors()[0])
				return False
		else:
			return True

	#####################################
	########## private methods ##########
	#####################################

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
		f = open(file,'r')
		dtd = f.read()
		f.close()
		return dtd

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
	cine = DOMDocumentCompanion()
	cine.parse("semaine10.xml", True)
	print(cine.doc.toxml())
	print(cine.getElementById('Ka'))
	print(cine.toLighter().toxml())