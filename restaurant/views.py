from django.shortcuts import render
import random
import time
def main(request):
    return render(request, 'restaurant/main.html')

def order(request):
    daily_special = random.choice(['Buffalo Chicken Wings','BBR Chicken Wings','Honey Garlic Chicken Wings','Teriyaki Chicken Wings','Lemon Pepper Chicken Wings'])
    context = {'daily_special': daily_special}
    return render(request, 'restaurant/order.html', context)


def confirmation(request):
    if request.method == 'POST':
        # Get the form data
        customer_name = request.POST.get('name')
        customer_phone = request.POST.get('phone')
        customer_email = request.POST.get('email')
        special_instructions = request.POST.get('instructions')
        items_ordered = request.POST.getlist('items')
        print(items_ordered)
        

        prices = {'Pizza': 12, 'Burger': 10, 'Pasta': 8, 'Salad': 7}
        total_price = sum([prices[item] for item in items_ordered if item in prices])   

        ready_in_minutes = random.randint(30, 60)
        ready_time = time.strftime('%a %b %d %H:%M:%S %Y', time.localtime(time.time() + ready_in_minutes * 60))

        context = {
            'customer_name': customer_name,
            'items_ordered': items_ordered,
            'total_price': total_price,
            'ready_time': ready_time,
            'customer_phone': customer_phone,
            'customer_email': customer_email,
            'special_instructions': special_instructions,
        }
        return render(request, 'restaurant/confirmation.html', context)
    else:
        return render(request, 'restaurant/order.html')
