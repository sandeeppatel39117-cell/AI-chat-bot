# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse
# # def home(request):
# #     return HttpResponse("<h1>Hey I am Django server</h1>...")

# def home(request):
#     return render(request,"/index.html")

# def success_page(request):
#     print("hit success page")
#     return HttpResponse("this is a success page...")







import os
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from dotenv import load_dotenv
from groq import Groq
import logging
logger = logging.getLogger(__name__)

load_dotenv()


def index(request):
    return render(request, "index.html")


@require_POST
@csrf_protect
def chat(request):
    print("hit chat request ...")
    try:
        data = json.loads(request.body)
        print("request",data)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse(
                {"error": "Please enter a message."},
                status=400
            )

        if len(message) > 4000:
            return JsonResponse(
                {"error": "Message is too long."},
                status=400
            )

        api_key = os.getenv("GROQ_API_KEY")
        # print("api_key:",api_key)
        if not api_key:
            return JsonResponse(
                {"error": "GROQ_API_KEY is missing in .env"},
                status=500
            )

        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Reply in the language used by the user."
                    )
                },
                {"role": "user", "content": message}
            ],
            max_completion_tokens=1000
        )

        reply = completion.choices[0].message.content

        return JsonResponse({"reply": reply})

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400
        )
    except Exception:
        logger.exception("Groq chatbot request failed")
        return JsonResponse(
            {"error": "Chat request failed. Check API key, model and server logs."},
            status=500
        )
