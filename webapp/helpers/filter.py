from babel.dates import format_date

def convert_to_id_date(value):
    if not value:
        return "-"
    return format_date(value, "d MMMM y", locale="id")