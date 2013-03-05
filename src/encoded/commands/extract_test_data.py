import loremipsum
import random
import re
import xlrd
from xlutils.filter import (
    BaseFilter,
    StreamWriter,
    XLRDReader,
    process,
    )


class SkipNonTests(BaseFilter):
    """Skip rows without a 'test' column value.
    """

    def sheet(self, rdsheet, wtsheet_name):
        self.rdsheet = rdsheet
        self.next.sheet(rdsheet, wtsheet_name)
        test_cols = [
            col for col in range(rdsheet.ncols)
            if rdsheet.cell_value(0, col).lower().strip() == 'test'
            ]
        if not test_cols:
            self.test_col = None
        else:
            self.test_col, = test_cols
        self.row_index = -1

    def row(self, rdrowx, wtrowx):
        if rdrowx == 0 or self.test_col is None \
            or self.rdsheet.cell_value(rdrowx, self.test_col):
            self.row_index += 1
            self.skip_row = False
            self.next.row(rdrowx, self.row_index)
        else:
            self.skip_row = True

    def cell(self, rdrowx, rdcolx, wtrowx, wtcolx):
        if not self.skip_row:
            self.next.cell(rdrowx, rdcolx, self.row_index, wtcolx)


def iter_rows(sheet):
    headers = [sheet.cell_value(0, col).lower().strip()
        for col in range(sheet.ncols)]
    for row in xrange(1, sheet.nrows):
        yield dict((name, sheet.cell(row, col))
                   for col, name in enumerate(headers) if name)


class Anonymize(BaseFilter):
    """Change email addresses, names and phone numbers
    """

    # From Colander. Not exhaustive, will not match .museum etc.
    email_re = re.compile(r'(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}')
    random_words = loremipsum._generator.words

    def __init__(self):
        self.mapped_emails = {}
        self.mapped_names = {}
        self.generated_emails = set()
        self.generated_names = set()

    def workbook(self, rdbook, wtbook_name):
        self.next.workbook(rdbook, wtbook_name)
        # PI names are public anyway
        colleagues = iter_rows(rdbook.sheet_by_name('colleague'))
        self.pi_names = set(row['last_name'].value.lower().strip()
            for row in colleagues if row['job_title'].value == 'PI')

    def sheet(self, rdsheet, wtsheet_name):
        wrapped_cell = rdsheet.cell

        def intercept_cell(rdrowx, rdcolx):
            cell = wrapped_cell(rdrowx, rdcolx)
            if not cell.value or rdrowx == 0:
                return cell

            # Replace all emails wherever they are
            if cell.ctype == xlrd.XL_CELL_TEXT:
                new_value, num_subs = self.email_re.subn(
                    self._replace_emails, cell.value)
                cell.value = new_value

            heading = wrapped_cell(0, rdcolx).value.lower().strip()
            if heading in ['fax', 'phone1', 'phone2']:
                cell.ctype = xlrd.XL_CELL_TEXT
                cell.value = '000-000-0000'

            elif heading in ['skype']:
                cell.ctype = xlrd.XL_CELL_TEXT
                cell.value = 'skypename'

            elif heading in ['last_name', 'submitted_by']:
                if cell.value.strip().lower() not in self.pi_names:
                    assert cell.ctype == xlrd.XL_CELL_TEXT
                    cell.value = self._replace_name(cell.value)

            elif heading in ['first_name']:
                cell.value = self._random_name(single=True)

            return cell

        rdsheet.cell = intercept_cell
        self.next.sheet(rdsheet, wtsheet_name)

    def _random_email(self):
        while True:
            generated = "%s.%s@%s.%s" % \
                tuple(random.choice(self.random_words) for n in range(4))
            if generated not in self.generated_emails:
                return generated

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

    def _random_name(self, single=False):
        while True:
            if single or random.choice(range(4)):
                generated = random.choice(self.random_words).capitalize()
            else:
                generated = "%s-%s" % \
                    tuple(random.choice(self.random_words).capitalize()
                        for n in range(2))
            if generated not in self.generated_names:
                return generated

    def _replace_name(self, name):
        found = name
        new, original = self.mapped_names.get(found.lower(), (None, None))
        if new is not None:
            if found != original:
                raise ValueError(
                    "Case mismatch for %s, %s" % (found, original))
            return new
        new = self._random_name()
        self.mapped_names[found.lower()] = (new, found)
        return new


def run(infile, outfile):
    wb = xlrd.open_workbook(file_contents=infile.read())
    reader = XLRDReader(wb, infile.name)
    writer = StreamWriter(outfile)
    process(reader, SkipNonTests(), Anonymize(), writer)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract test data set.')
    parser.add_argument('infile', type=argparse.FileType('rb'))
    parser.add_argument('outfile', type=argparse.FileType('wb'))
    args = parser.parse_args()
    run(args.infile, args.outfile)

if __name__ == '__main__':
    main()
