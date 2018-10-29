from django.shortcuts import render
from django.conf import settings
from django_telegrambot.apps import DjangoTelegramBot
from django.views.generic.base import View

# Create your views here.
def index(request):
    bot_list = DjangoTelegramBot.bots
    context = {'bot_list': bot_list, 'update_mode':settings.DJANGO_TELEGRAMBOT['MODE']}
    return render(request, 'bot/index.html', context)

def test(request):
    import json
    a = {'nombre': 'carlos'}
    return json.dumps(a)

class Login(View):
    def get(self, request):
        import json
        a = {'nombre': 'carlos'}
        return json.dumps(a)
