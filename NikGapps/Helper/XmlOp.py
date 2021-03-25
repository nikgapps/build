from xml.etree.cElementTree import Element, SubElement, ElementTree


class XmlOp:
    def __init__(self, package_name, permissions_list, import_path):
        self.root = Element("permissions")
        self.doc = SubElement(self.root, "privapp-permissions", package=package_name)
        for permission in permissions_list:
            SubElement(self.doc, "permission", name=permission)
        self.root = XmlOp.indent(self.root)
        self.tree = ElementTree(self.root)
        self.tree.write(import_path)

    @staticmethod
    def indent(elem, level=0):
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                XmlOp.indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem
