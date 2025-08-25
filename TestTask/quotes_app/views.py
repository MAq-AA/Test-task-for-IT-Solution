from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db import models
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect

from .forms import AddQuoteForm
from .models import Quote, Source, LikeDislike
from django.http import JsonResponse, HttpResponse
import random


def add_quote(request):
    if request.method == 'POST':
        form = AddQuoteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            source, created = Source.objects.get_or_create(name=data['source_name'])

            new_quote = Quote(
                text=data['text'],
                source=source,
                weight=data['weight']
            )
            new_quote.save()

            return redirect('add_quote')
    else:
        form = AddQuoteForm()

    return render(request, 'add_quote.html', {'form': form})


def home_page(request):
    selected_quote = weighted_random_quote()

    if selected_quote is None:
        return HttpResponse("Нет доступной цитаты.", status=404)

    if selected_quote:
        selected_quote.views_count += 1
        selected_quote.save()

    likes = selected_quote.likedislike_set.filter(value=1).aggregate(models.Sum('value'))['value__sum'] or 0
    dislikes = selected_quote.likedislike_set.filter(value=-1).aggregate(models.Sum('value'))['value__sum'] or 0

    context = {
        'likes': likes,
        'dislikes': abs(dislikes),
        'quote': selected_quote,
        'like_url': reverse('toggle_like_dislike', kwargs={'quote_id': selected_quote.id}),  # Передаем готовый URL
    }

    return render(request, 'home.html', context)


def weighted_random_quote():
    quotes = list(Quote.objects.all())
    if not quotes:
        return None

    total_weight = sum(quote.weight for quote in quotes)
    rand_val = random.uniform(0, total_weight)
    current_sum = 0
    for quote in quotes:
        current_sum += quote.weight
        if current_sum > rand_val:
            return quote
    return None


def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация',
                    'redirect_url': reverse('login') + f'?next={request.path}'
                }, status=401)
            else:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.path)
        return view_func(request, *args, **kwargs)
    return wrapper

@ajax_login_required
@require_POST
@csrf_exempt
def toggle_like_dislike(request, quote_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация',
            'redirect_url': reverse('login')  # Добавляем URL для редиректа
        })

    try:
        quote = Quote.objects.get(id=quote_id)
        action = request.POST.get('action')


        like_dislike, created = LikeDislike.objects.get_or_create(
            user=request.user,
            quote=quote,
            defaults={'value': 1 if action == 'like' else -1}
        )

        if not created:
            if like_dislike.value == (1 if action == 'like' else -1):
                like_dislike.delete()
                user_vote = 0
            else:
                like_dislike.value = 1 if action == 'like' else -1
                like_dislike.save()
                user_vote = like_dislike.value
        else:
            user_vote = like_dislike.value

        likes = quote.likedislike_set.filter(value=1).count()
        dislikes = quote.likedislike_set.filter(value=-1).count()

        return JsonResponse({
            'success': True,
            'likes': likes,
            'dislikes': dislikes,
            'user_vote': user_vote
        })

    except Quote.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Цитата не найдена'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def popular_quotes(request):
    top_quotes = Quote.objects.annotate(total_likes=models.Sum('likedislike__value')).order_by('-total_likes')[:10]
    return render(request, 'popular_quotes.html', {'top_quotes': top_quotes})
