# projectus\views\register.py

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from projectus.forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = RegisterForm()

    return render(
        request,
        'projectus/register.html',
        {'form': form}
    )