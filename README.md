# epub2json
epub2json.py can convert epub files to JSON using a modified BadgerFish (http://badgerfish.ning.com/) convention 
```Shell
epub2json.py georgia-cfi.epub georgia-cfi.json
```
Would convert georgia-cfi.epub (for instance, the one available at http://idpf.github.io/epub3-samples/samples.html) 
to a JSON file containing all data needed to display the contents. Binary data such as images are base64-encoded.
Example of cover.xhtml in JSON after extracting from the above epub:
```JSON
"cover": {
        "media_type": "application/xhtml+xml", 
        "href": "cover.xhtml", 
        "$": {
            "html": {
                "@xmlns": "http://www.w3.org/1999/xhtml", 
                "@xml:lang": "en-US", 
                "@lang": "en-US", 
                "head": {
                    "title": {
                        "$": "ENCYCLOPAEDIA BRITANNICA"
                    }, 
                    "link": {
                        "@rel": "stylesheet", 
                        "@type": "text/css", 
                        "@href": "css/epub.css"
                    }, 
                    "meta": {
                        "@charset": "utf-8"
                    }
                }, 
                "body": {
                    "img": {
                        "@src": "images/cover.png", 
                        "@alt": "Cover Image"
                    }
                }
            }
        }
```
Alternatively, pass the --binary-zip option to save non-text data in a separate zip file:
```Shell
epub2json.py georgia-cfi.epub georgia-cfi.json --binary-zip georgia-cfi.zip
```
