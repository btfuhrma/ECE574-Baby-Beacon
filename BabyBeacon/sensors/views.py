from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData, UserAPIKey
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

# Create your views here.
@csrf_exempt
def sensorData(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        api_key = data.get('api_key')
        temp = data.get('temperature')
        amp = data.get('amplitude')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not api_key:
        return JsonResponse({'error': 'Missing API key'}, status=401)

    try:
        user_api = UserAPIKey.objects.get(key=api_key, active=True)
    except UserAPIKey.DoesNotExist:
        return JsonResponse({'error': 'Invalid API key'}, status=401)

    SensorData.objects.create(
        user=user_api.user,
        temperature_c=temp,
        amplitude=amp
    )
    print(temp, amp, user_api.user.username)
    return JsonResponse({'status': 'success'})

def getToken(request):
    api_key = UserAPIKey.objects.filter(active=True).first()
    
    if api_key:
        return JsonResponse({'api_key': api_key.key})
    return JsonResponse({'api_key': None})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            api_key, created = UserAPIKey.objects.get_or_create(user=user)
            api_key.active = True
            api_key.save()

            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

def getLatestData(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    latest_data = SensorData.objects.filter(user=request.user).order_by('-timestamp').first()
    history = SensorData.objects.filter(user=request.user).order_by('-timestamp')[:20][::-1]
    if latest_data:
        data = {
            'temperature_c': latest_data.temperature_c,
            'amplitude': latest_data.amplitude,
            'threshold_temp': 30,  # you can make these configurable
            'threshold_amp': 8,
            'temp_history': [d.temperature_c for d in history],
            'amp_history': [d.amplitude for d in history],
            'labels': [d.timestamp.strftime('%H:%M') for d in history]
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'No data found'}, status=404)

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password1', '').strip()

        user = User.objects.create_user(username=username, password=password)
        user.save()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)

            api_key, created = UserAPIKey.objects.get_or_create(user=user)
            api_key.active = True
            api_key.save()

            return redirect('dashboard')  

    return render(request, 'users/signup.html')

def logout(request):
    if request.user.is_authenticated:
        UserAPIKey.objects.filter(user=request.user).update(active=False)
    auth_logout(request)
    return redirect('user_login')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    return render(request, 'sensors/dashboard.html')
