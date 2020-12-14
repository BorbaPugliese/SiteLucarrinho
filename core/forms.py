from django import forms


ENVIO_CHOICES = (
    ('W', 'Whatsapp'),
    ('E', 'Email')
)


class CheckoutForm(forms.Form):
    envio_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=ENVIO_CHOICES)


