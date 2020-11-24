#!/usr/bin/python

from xml.dom.minidom import Node, Element, parse
import re


def purgeDOM(no, del_spaces = True, del_comments = True, del_pi = True) :
	if no.nodeType == Node.ELEMENT_NODE :
		toDel = []
		for n in no.childNodes :
			if del_spaces and n.nodeType == Node.TEXT_NODE and n.data.strip('\t \n') == '' :
				toDel.append(n)
			elif del_comments and n.nodeType == Node.COMMENT_NODE :
				toDel.append(n)
			elif del_pi and n.nodeType == Node.PROCESSING_INSTRUCTION_NODE :
				toDel.append(n)
			elif n.nodeType == Node.ELEMENT_NODE :
				purgeDOM(n,del_spaces,del_comments, del_pi)
		for n in toDel :
			no.removeChild(n)
	elif no.nodeType == Node.DOCUMENT_NODE :
		for n in no.childNodes :
			purgeDOM(n,del_spaces,del_comments, del_pi)
	elif no.nodeType == Node.DOCUMENT_TYPE_NODE :
		pass
	else :
		pass
	return no

def getDTD(file) :
	f = open(file,'r')
	dtd = f.read()
	f.close()
	return dtd

def extractDTD(file) :

	el = re.compile(r'<!ELEMENT (?P<elementname>[\w\-\:\_]+) (?P<description>.*)\s*>')
	att = re.compile(r'<!ATTLIST (?P<elementname>[\w\-\:\_]+) (?P<attributs>.*)\s*>')
	att2 = re.compile(r'(?P<attname>[\w\-\:\_]+) (?P<def>.*?) (?P<status>#[\w\-\:\_]+|[\"\'].*?[\"\'])')
	comment = re.compile(r'<!-- \.*? -->')

	dtd = getDTD(file).replace('\n',' ').replace('\t',' ')
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

def enrichNode(node, le) :
	if node.nodeType == Node.ELEMENT_NODE :
		la = le[node.tagName]
		for (att, (definition, status)) in la.items() :
			if node.hasAttribute(att) :
				pass
			else :
				if '#' not in status :
					node.setAttribute(att,status) 
		for n in node.childNodes :
			enrichNode(n,le)

def enrichXML(doc) :
	dtdFile = doc.doctype.systemId
	if dtdFile is not None :
		#print(dtdFile)
		le = extractDTD(dtdFile)
		enrichNode(doc.documentElement, le)


if ( __name__ == "__main__"):
	doc = parse("semaine10.xml")
	#purgeDOM(doc)

	enrichXML(doc)
	print(doc.toxml())
