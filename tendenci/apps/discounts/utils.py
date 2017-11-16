from decimal import Decimal

def assign_discount(price_list, discount):
    """Given a list of prices and a discount object,
       return a discount applied price list, discount total,
       a list of discount amount, and the message.
       If the available count number of uses < len(price_list),
       apply the discount to the highest price first.
    """

    limit = 0
    msg = ''
    if discount.cap != 0:
        limit = discount.cap - discount.num_of_uses()
        if limit <= 0:
            return price_list, 0, [], ''

    sorted_prices = [(index, value) for index, value in enumerate(price_list)]
    sorted_prices.sort(key=lambda x: x[1])
    sorted_prices.reverse()

    discount_value = discount.value

    count = len(price_list)
    if limit != 0 and limit < len(price_list):
        count = limit
        msg = 'Discount is only available for %s. ' % count

    discount_total = Decimal(0)
    discount_list = [Decimal(0) for i in range(len(price_list))]    # a list of discount amount applied
    for index, value in sorted_prices:
        if count == 0:
            break

        if price_list[index] > discount_value:
            val = price_list[index] - discount_value
            discount_total += discount_value
            discount_list[index] = discount_value
        else:
            val = Decimal('0.00')
            discount_total += price_list[index]
            discount_list[index] = price_list[index]

        price_list[index] = val
        count -= 1

    return price_list, discount_total, discount_list, msg
