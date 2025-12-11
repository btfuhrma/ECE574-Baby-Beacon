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

def statistics(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    user_data = SensorData.objects.filter(user=request.user).order_by('timestamp')
    
    if not user_data.exists():
        return render(request, 'sensors/statistics.html', {'error': 'No data available.'})

    temp_threshold = float(request.GET.get('temp_threshold', 30))
    amp_threshold = float(request.GET.get('amp_threshold', 8))

    spikes = [d for d in user_data if d.temperature_c >= temp_threshold or d.amplitude >= amp_threshold]

    num_spikes = len(spikes)
    max_amp = max([d.amplitude for d in spikes], default=0)

    avg_time_between_spikes = None
    if len(spikes) > 1:
        spikes_sorted = sorted(spikes, key=lambda d: d.timestamp)
        deltas = [(t2.timestamp - t1.timestamp).total_seconds() 
                  for t1, t2 in zip(spikes_sorted[:-1], spikes_sorted[1:])]
        avg_time_between_spikes = sum(deltas) / len(deltas)

    recent_readings = user_data.order_by('-timestamp')[:5]

    context = {
        'recent_spikes': recent_readings,
        'num_spikes': num_spikes,
        'max_amp': max_amp,
        'avg_time_between_spikes': avg_time_between_spikes,
        'current_temp_threshold': temp_threshold,
        'current_amp_threshold': amp_threshold,
    }

    return render(request, 'sensors/statistics.html', context)

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
