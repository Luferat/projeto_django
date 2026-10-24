# projectus\views\password_reset.py

from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, redirect
from django import forms


class PasswordResetForm(forms.Form):
    username = forms.CharField(label='Nome de usuário')


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                form.add_error(
                    'username',
                    'Usuário não encontrado.'
                )
            else:
                return redirect(
                    'password_reset_confirm',
                    username=user.username
                )

    else:
        form = PasswordResetForm()

    return render(
        request,
        'projectus/password_reset.html',
        {'form': form}
    )


def password_reset_confirm(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('password_reset')

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        'projectus/password_reset_confirm.html',
        {'form': form}
    )
