import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = r"Scope.docx"

if not os.path.exists(docx_path):
    print(f"Error: {docx_path} does not exist.")
    exit(1)

try:
    with zipfile.ZipFile(docx_path) as docx:
        # The main body of the document is in word/document.xml
        xml_content = docx.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # Word XML namespaces
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Extract all paragraphs
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append("".join(texts))
            else:
                paragraphs.append("")
                
        # Join paragraphs with double newlines
        print("\n".join(paragraphs))
except Exception as e:
    print(f"Error reading docx: {e}")
