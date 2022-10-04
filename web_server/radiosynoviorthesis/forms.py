from django import forms
from django.core.validators import MinValueValidator


class CalculatorForm(forms.Form):

    ISOTOPES_OPTIONS = (
        ('Y-90', 1),
        ('P-32', 2),
        ('Re-188', 3),
        ('Re-186', 4),
        ('Sm-153', 5),
        ('Lu-177', 6),
    )

    THICKNESS_OPTIONS = (
        ('1', 1),
        ('2', 2),
        ('3', 3),
    )

    radionuclide = forms.ChoiceField(choices=ISOTOPES_OPTIONS)
    thickness = forms.ChoiceField(choices=THICKNESS_OPTIONS)
    surface = forms.FloatField(validators=[MinValueValidator(0.0)])

    def clean_thickness(self):
        thickness = self.cleaned_data['thickness']

        return f'{thickness} mm'
