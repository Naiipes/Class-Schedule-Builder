from datetime import datetime
from openpyxl import load_workbook
from catalog.csv_importer import CsvCatalogImporter

class ExcelCatalogImporter(CsvCatalogImporter):
    def read_rows(self) -> list[dict]:
        workbook = load_workbook(self.path, read_only=True, data_only=True)
        sheet = workbook.active
        all_rows = list(sheet.iter_rows(values_only=True))
        workbook.close()

        headers = all_rows[0]
        rows = []

        for values in all_rows[1:]:
            row = {}

            for i in range(len(headers)):
                value = values[i]

                if value is None:
                    value = ""
                elif isinstance(value, datetime):
                    value = value.strftime("%m/%d/%Y")
                row[str(headers[i])] = str(value)

            rows.append(row)

        return rows