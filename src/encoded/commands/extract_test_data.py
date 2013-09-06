import csv
import loremipsum
import random
import re
from ..loadxl import *


class Anonymizer(object):
    """Change email addresses and names consistently
    """

    # From Colander. Not exhaustive, will not match .museum etc.
    email_re = re.compile(r'(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}')
    random_words = loremipsum._generator.words

    def __init__(self):
        self.mapped_emails = {}
        self.mapped_names = {}
        self.generated_emails = set()
        self.generated_names = set()

    def replace_emails(self, dictrows):
        for row in dictrows:
            for k, v in list(row.iteritems()):
                if v is None:
                    continue
                new_value, num_subs = self.email_re.subn(
                    self._replace_emails, v)
                row[k] = new_value
            yield row

    def replace_non_pi_names(self, dictrows):
        for row in dictrows:
            if row.get('job_title') != 'PI':
                if 'first_name' in row:
                    row['first_name'] = random.choice(self.random_words).capitalize()
                if 'last_name' in row:
                    row['last_name'] = self._random_name()
            yield row

    def _random_email(self):
        for _ in xrange(1000):
            generated = "%s.%s@%s.%s" % \
                tuple(random.choice(self.random_words) for n in range(4))
            if generated not in self.generated_emails:
                self.generated_emails.add(generated)
                return generated
        raise AssertionError("Unable to find random email")

    def _replace_emails(self, matchobj):
        found = matchobj.group(0)
        new, original = self.mapped_emails.get(found.lower(), (None, None))
        if new is not None:
            if found != original:
                raise ValueError(
                    "Case mismatch for %s, %s" % (found, original))
            return new
        new = self._random_email()
        self.mapped_emails[found.lower()] = (new, found)
        return new

    def _random_name(self):
        for _ in xrange(1000):
            if random.choice(range(4)):
                generated = random.choice(self.random_words).capitalize()
            else:
                generated = "%s-%s" % \
                    tuple(random.choice(self.random_words).capitalize()
                            for n in range(2))
            if generated not in self.generated_names:
                self.generated_names.add(generated)
                return generated
        raise AssertionError("Unable to find random name")


def set_existing_key_value(**kw):
    def component(dictrows):
        for row in dictrows:
            for k, v in kw.iteritems():
                if k in row:
                    row[k] = v
            yield row

    return component


def drop_rows_with_all_key_value(**kw):
    def component(dictrows):
        for row in dictrows:
            if not all(row[k] == v if k in row else False for k, v in kw.iteritems()):
                yield row

    return component


def extract_pipeline():
    return [
        skip_rows_with_all_falsey_value('test'),
        skip_rows_with_all_key_value(test='skip'),
        skip_rows_with_all_falsey_value('test'),
        skip_rows_missing_all_keys('uuid'),
        drop_rows_with_all_key_value(_skip=True),
    ]

def anon_pipeline():
    anonymizer = Anonymizer()
    return extract_pipeline() + [
        set_existing_key_value(
            fax='000-000-0000',
            phone1='000-000-0000',
            phone2='000-000-0000',
            skype='skype',
            google='google',
        ),
        anonymizer.replace_emails,
        anonymizer.replace_non_pi_names,
    ]


def run(pipeline, inpath, outpath):
    for item_type in ORDER:
        source = read_single_sheet(inpath, item_type)
        fieldnames = [k for k in source.fieldnames if ':ignore' not in k]
        with open(os.path.join(outpath, item_type + '.tsv'), 'wb') as out:
            writer = csv.DictWriter(out, fieldnames, dialect='excel-tab', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(combine(source, pipeline))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract test data set.')
    parser.add_argument('--anonymize', '-a', action="store_true",
        help="anonymize the data.")
    parser.add_argument('inpath',
        help="input zip file of excel sheets.")
    parser.add_argument('outpath',
        help="directory to write filtered tsv files to.")
    args = parser.parse_args()
    pipeline = anon_pipeline() if args.anonymize else extract_pipeline()
    import pdb
    import sys
    import traceback
    try:
        run(pipeline, args.inpath, args.outpath)
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

if __name__ == '__main__':
    main()
