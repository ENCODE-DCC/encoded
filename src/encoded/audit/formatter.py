import re

def audit_link(linkText, uri):
    """Generate link "markdown" from URI."""
    return '{{{}|{}}}'.format(linkText, uri)

def path_to_text(path):
    """Convert object path to the text portion."""
    accession = re.match(r'\/.*\/(.*)\/', path)
    return accession.group(1) if accession else None

def space_in_words(objects_string):
    """Insert a space between objects that have more than one
    capital letter eg. AntibodyChar --> Antibody Char"""
    add_space = re.sub(r"(\w)([A-Z])", r"\1 \2", objects_string)
    return add_space
