from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User



    def user_login(request):
    print("View hit")
    if request.method == 'POST':
        print("POST received") 
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Incorrect username or password.")  

    return render(request, 'users/login.html')


    def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'signup.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'signup.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'signup.html')

        # Create the user
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('user_login')  # replace with your login URL name

    return render(request, 'signup.html')