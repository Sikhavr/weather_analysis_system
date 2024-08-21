from django.shortcuts import render

import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WeatherData
from .serializers import WeatherDataSerializer

class WeatherAPIView(APIView):
    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response({"error": "City parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        api_key = 'b19e3afbd37a4fd9aff55943242108'
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or 'error' in data:
            return Response({"error": "Unable to fetch weather data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        weather_data = WeatherData(
            city=city,
            temperature=data['current']['temp_c'],
            humidity=data['current']['humidity'],
            description=data['current']['condition']['text']
        )
        weather_data.save()

        alert = ""
        if weather_data.temperature > 35:
            alert = "Extreme heat alert!"
        elif weather_data.temperature >20:
            alert = "Moderate Climate"
        elif weather_data.temperature < 0:
            alert = "Extreme cold alert!"

        serializer = WeatherDataSerializer(weather_data)
        response_data = serializer.data
        response_data['alert'] = alert

        return Response(response_data, status=status.HTTP_200_OK)
