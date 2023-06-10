from django import forms

from poli.models import Poli


class DownloadForm(forms.Form):
    try:
        choices = [(i, j) for i, j in enumerate(['全部'] + [i['City'] for i in Poli.objects.values('City').distinct()])]
    except Exception:
        choices = [(0,'全部')]

    City = forms.ChoiceField(choices=choices, label='城市')

