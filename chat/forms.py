from django import forms
from .models import Discussion

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de la discussion'})
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("Le titre est obligatoire.")
        return title
