from django import forms
from .models import Quote, Source

class AddQuoteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    source_name = forms.CharField(label='Источник')
    weight = forms.IntegerField(min_value=1, initial=1)

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if text:
            if Quote.objects.filter(text__iexact=text).exists():
                raise forms.ValidationError("Такая цитата уже существует.")

            normalized_text = ' '.join(text.strip().split())
            if Quote.objects.filter(text__iexact=normalized_text).exists():
                raise forms.ValidationError("Такая цитата уже существует (с учетом форматирования).")

        return text

    def clean_source_name(self):
        source_name = self.cleaned_data.get('source_name')

        if source_name:
            try:
                source = Source.objects.get(name=source_name)
                if Quote.objects.filter(source=source).count() >= 3:
                    raise forms.ValidationError("У источника уже три цитаты.")
            except Source.DoesNotExist:
                pass

        return source_name