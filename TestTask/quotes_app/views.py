from functools import wraps
from django.db import models
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AddQuoteForm
from .models import Quote, Source, LikeDislike
from django.http import JsonResponse
import random
from django.utils.http import url_has_allowed_host_and_scheme


def get_safe_redirect_url(request, default_url=None):
    next_url = request.GET.get('next') or request.session.get('next_url')

    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return next_url
    return default_url


def add_quote(request):
    if not request.user.is_authenticated:
        request.session['next_url'] = request.get_full_path()
        return redirect('login')

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
            messages.success(request, 'Цитата успешно добавлена')

            if 'next_url' in request.session:
                del request.session['next_url']
            return redirect('add_quote')
    else:
        form = AddQuoteForm()

    return render(request, 'add_quote.html', {'form': form})


def home_page(request):
    selected_quote = weighted_random_quote()

    if selected_quote is None:
        return render(request, 'base.html')

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
    quotes = Quote.objects.all()
    if not quotes:
        return None

    weights = [quote.weight for quote in quotes]
    return random.choices(quotes, weights=weights, k=1)[0]


@require_POST
@csrf_exempt
def toggle_like_dislike(request, quote_id):
    if not request.user.is_authenticated:
        request.session['next_url'] = request.META.get('HTTP_REFERER', '/')
        login_url = f"{reverse('login')}"

        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация',
            'redirect_url': login_url
        }, status=401)

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
    top_quotes = Quote.objects.annotate(total_likes=models.Sum('likedislike__value', default=0)).order_by('-total_likes')[:10]
    return render(request, 'popular_quotes.html', {'top_quotes': top_quotes})
