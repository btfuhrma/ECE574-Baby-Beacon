from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SensorData, UserAPIKey

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
    return JsonResponse({'status': 'success'})
    return

def getToken(request):
    api_key = UserAPIKey.objects.filter(active=True).first()
    
    if api_key:
        return JsonResponse({'api_key': api_key.key})
    return JsonResponse({'api_key': None})