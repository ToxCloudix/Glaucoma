from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/glaucoma/home')
        else:
            return JsonResponse({'message': 'Invalid username or password'}, status=401)
        
    return render(request, 'authentication/login.html')
