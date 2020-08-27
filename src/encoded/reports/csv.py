import csv


class CSVGenerator:

    def __init__(self, delimiter='\t', lineterminator='\n'):
        self.writer = csv.writer(
            self,
            delimiter=delimiter,
            lineterminator=lineterminator
        )

    def writerow(self, row):
        self.writer.writerow(row)
        return self.row

    def write(self, row):
        self.row = row.encode('utf-8')
