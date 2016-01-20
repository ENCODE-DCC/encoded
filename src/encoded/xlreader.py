"""csv compatible interface for xlrd sheets
"""

import csv
import datetime
import os.path
import xlrd
import zipfile


def cell_value(cell, datemode):
    ctype = cell.ctype
    value = cell.value

    if ctype == xlrd.XL_CELL_ERROR:
        raise ValueError(repr(cell), 'cell error')

    elif ctype == xlrd.XL_CELL_BOOLEAN:
        return str(value).upper()

    elif ctype == xlrd.XL_CELL_NUMBER:
        if value.is_integer():
            value = int(value)
        return str(value)

    elif ctype == xlrd.XL_CELL_DATE:
        value = xlrd.xldate_as_tuple(value, datemode)
        if value[3:] == (0, 0, 0):
            return datetime.date(*value[:3]).isoformat()
        else:
            return datetime.datetime(*value).isoformat()

    elif ctype in (xlrd.XL_CELL_TEXT, xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return value

    raise ValueError(repr(cell), 'unknown cell type')



def reader(stream, sheetname=None):
    """ Read named sheet or first and only sheet from xlsx file
    """
    book = xlrd.open_workbook(file_contents=stream.read())
    if sheetname is None:
        sheet, = book.sheets()        
    else:
        try:
            sheet = book.sheet_by_name(sheetname)
        except xlrd.XLRDError:
            return

    datemode = sheet.book.datemode
    for index in range(sheet.nrows):
        yield [cell_value(cell, datemode) for cell in sheet.row(index)]


class DictReader:
    # Adapted from http://hg.python.org/cpython/file/2.7/Lib/csv.py
    def __init__(self, stream, fieldnames=None, restkey=None, restval=None,
                 *args, **kwds):
        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.reader = reader(stream, *args, **kwds)
        self.line_num = 0

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
            else:
                self.line_num += 1
        #self.line_num = self.reader.line_num
        return self._fieldnames

    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value

    def __next__(self):
        if self._fieldnames is None:
            # Used only for its side effect.
            self.fieldnames
        row = next(self.reader)
        self.line_num += 1

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        if lf < lr:
            d[self.restkey] = row[lf:]
        elif lf > lr:
            for key in self.fieldnames[lr:]:
                d[key] = self.restval
        return d


def zipfile_to_csv(zipfilename, outpath, ext='.csv', dialect='excel', **fmtparams):
    """ For Google Drive download zips
    """
    zf = ZipFile(zipfilename)
    for name in zf.namelist():
        subpath, entry_ext = os.path.splitext(name)
        if entry_ext.lower() != '.xlsx':
            continue
        f = zf.open(name)
        book = xlrd.open_workbook(file_contents=f.read())
        sheet, = book.sheets()  # Only single worksheet books are handled
        csvfile = open(os.path.join(outpath, subpath + ext), 'w')
        wr = csv.writer(csvfile, dialect=dialect, **fmtparams)
        wr.writerows(list(reader(sheet)))

