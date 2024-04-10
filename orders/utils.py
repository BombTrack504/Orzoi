import datetime
import simplejson as json


def create_ord_num(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_numb = current_datetime + str(pk)
    return order_numb


def order_total_by_res(order, restaurant_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(restaurant_id))
    subtotal = 0
    tax = 0
    tax_dict = {}

    for key, value in data.items():
        # print(key, value)
        subtotal += float(key)
        value = value.replace("'", '"')
        value = json.loads(value)
        tax_dict.update(value)
        # print(subtotal, tax_dict)
        # for tax calculation
        # 60.0 {'VAT': {'13.00': '7.80'}}
        for i in value:
            # print(i)
            for j in value[i]:
                # print(value[i][j])
                tax += float(value[i][j])
    grand_total = float(subtotal) + float(tax)
    context = {
        'subtotal': subtotal,
        'tax_dict': tax_dict,
        'grand_total': grand_total,
    }
    return context
