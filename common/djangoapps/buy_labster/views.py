from django.shortcuts import render_to_response
from django.views import generic
from buy_labster.forms import PaymentForm
from django.core.urlresolvers import reverse


def buy_lab(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)

        context = {
            'banana': 'banana',
        }

        if form.is_valid():  # charges the card
            return render_to_response("buy_lab.html", context)
    else:
        form = PaymentForm()
        context = {
            'form': form,
        }

    return render_to_response("buy_lab.html", context)