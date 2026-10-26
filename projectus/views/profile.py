# projectus/views/profile.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from projectus.forms import ProfileForm


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil salvo com sucesso!')
            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        'projectus/profile.html',
        {'form': form}
    )
