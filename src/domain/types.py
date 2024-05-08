from datetime import date

class TypeFormatter:
    @staticmethod
    def convert_date_to_ymd(dt: date):
        return dt.strftime("%Y-%m-%d")