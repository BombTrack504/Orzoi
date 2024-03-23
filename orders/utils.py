import datetime


def create_ord_num(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_numb = current_datetime + str(pk)
    return order_numb
