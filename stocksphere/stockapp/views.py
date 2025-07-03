from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')

# views.py
import requests
from django.http import JsonResponse
from django.conf import settings

def get_general_stock_news(request):
    """
    Fetch general stock news from NewsAPI and return it as JSON response.
    """
    try:
        # Replace 'q=stocks' with any query as per your requirement
        url = f"https://newsapi.org/v2/everything?q=stocks&language=en&sortBy=publishedAt&apiKey={settings.NEWSAPI_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "ok":
            news = [
                {
                    "published": article["publishedAt"],
                    "title": article["title"],
                    "url": article["url"],
                    "summary": article["description"] or "No summary available."
                }
                for article in data.get("articles", [])
            ]
            return JsonResponse({"news": news})
        else:
            return JsonResponse({"error": "Failed to fetch news from NewsAPI."}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({'error': str(e)}, status=500)
