import re

def audit_link(linkText, uri):
    """Generate link "markdown" from URI."""
    return '{{{}|{}}}'.format(linkText, uri)

def path_to_text(path):
    """Convert object path to the text portion."""
    accession = re.match('\/.*\/(.*)\/', path)
    return accession.group(1) if accession else None
