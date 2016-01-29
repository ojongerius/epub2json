#!/usr/bin/python
import epub
import lxml.html
from xmljson import BadgerFish, XMLData
import json
from collections import Counter, OrderedDict
from base64 import b64encode
import argparse
from zipfile import ZipFile

parser = argparse.ArgumentParser(description="Convert epub books to JSON")
parser.add_argument('epub_source',
    help='the epub document to convert')
parser.add_argument('destination',
    help='file name to write JSON to')
parser.add_argument('--binary-zip', dest='zipfile',
    help='instead of base64 encoding binary data, write it to this zip file instead')

args = parser.parse_args()

book = epub.open_epub(args.epub_source)
# Extend BadgerFish rules (http://badgerfish.ning.com/) to
# - add tail properties from lxml as $2
# - removes stripping of whitespace around text as this may be needed
#   when displaying the book
class ExtBadgerFish(BadgerFish):
    def data(self, root):
        'Convert etree.Element into a dictionary'
        value = self.dict()
        children = [node for node in root if isinstance(node.tag, basestring)]
        for attr, attrval in root.attrib.items():
            attr = attr if self.attr_prefix is None else self.attr_prefix + attr
            value[attr] = self._convert(attrval)
        if root.text and self.text_content is not None:
            text = root.text.strip()
            if text:
                if self.simple_text and len(children) == len(root.attrib) == 0:
                    value = self._convert(text)
                else:
                    value[self.text_content] = self._convert(text)
		if root.tail:
			value["$2"] = self._convert(root.tail)
        count = Counter(child.tag for child in children)
        for child in children:
            if count[child.tag] == 1:
                value.update(self.data(child))
            else:
                result = value.setdefault(child.tag, self.list())
                result += self.data(child).values()
        return self.dict([(root.tag, value)])

ext_bf = ExtBadgerFish(dict_type=OrderedDict)

#TODO: move to unit test		
#data = """<html> <body> <p version="1.0"> "hi there <em> you </em> how are <em> you </em> today?"  </p> </body> </html>"""
#html = lxml.html.document_fromstring(data)
#print json.dumps(ext_bf.data(html), indent=4)

# Ref: http://www.idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.4
# Get a list of the elements in the spine, and traverse them in order
final_return = OrderedDict()
final_return["spine"] = OrderedDict()
for itemref, linear in book.opf.spine.itemrefs:
    final_return["spine"][itemref] = linear
    
def add_data_to_return(ret, id, item, encoded_data):
    if(encoded_data):
        ret[id] = {
            "media_type" : item.media_type,
            "href" : item.href,
            "$" : encoded_data
        }
    else:
        ret[id] = {
            "media_type" : item.media_type,
            "href" : item.href,
        }

if(args.zipfile):
    zip = ZipFile(args.zipfile, "w")
manifest = book.opf.manifest
for id in manifest:
    item = manifest[id]
    data = book.read_item(item)  
    if item.media_type == u'application/xhtml+xml':
        html = lxml.html.document_fromstring(data)
        encoded_data = ext_bf.data(html)
    elif "text/" in item.media_type:
        encoded_data = data
    else:
        if(args.zipfile):
            zip.writestr(item.href, data)
            encoded_data = None
        else:
            encoded_data = b64encode(data)
    add_data_to_return(final_return, id, item, encoded_data)
if(args.zipfile):
    zip.close()
open(args.destination, "w").write(json.dumps(final_return, indent=4))
