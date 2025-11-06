from django import forms
from dashboard.models import Reuniao

class ReuniaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garante que o campo data renderize e aceite formato ISO (YYYY-MM-DD)
        self.fields['data'].widget = forms.DateInput(
            attrs={'type': 'date'}, format='%Y-%m-%d'
        )
        self.fields['data'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']

    class Meta:
        model = Reuniao
        # Removido 'status' dos fields para usar o default do model e não exigir input no formulário
        fields = ['titulo', 'objetivo', 'data', 'hora', 'local', 'participantes', 'anexos', 'planta', 'recorrencia', 'observacoes']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            # Força classe para padronizar tema escuro nas combobox
            'planta': forms.Select(attrs={'class': 'form-control dark-select'}),
            'recorrencia': forms.Select(attrs={'class': 'form-control dark-select'}),
            'anexos': forms.ClearableFileInput(),
            'objetivo': forms.Textarea(attrs={'rows':2}),
            'observacoes': forms.Textarea(attrs={'rows':2}),
        }
