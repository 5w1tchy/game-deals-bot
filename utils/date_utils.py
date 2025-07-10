import datetime


def get_next_month_year():
    today = datetime.date.today()
    first_of_next_month = (today.replace(
        day=1) + datetime.timedelta(days=32)).replace(day=1)
    return first_of_next_month.strftime("%B"), first_of_next_month.year
