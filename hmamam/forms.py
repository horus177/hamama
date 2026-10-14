from django import forms
from .models import ProductionRecord,  PigeonPair


class DailyRecordForm(forms.ModelForm):
    class Meta:
        model = ProductionRecord
        fields = ['eggs_found', 'squabs_hatched', 'deaths']
        
        # بنضيف كلاسات Bootstrap عشان شكلها يكون حلو على الموبايل
        widgets = {
            'eggs_found': forms.NumberInput(attrs={'class': 'form-control form-control-lg text-center', 'min': '0'}),
            'squabs_hatched': forms.NumberInput(attrs={'class': 'form-control form-control-lg text-center', 'min': '0'}),
            'deaths': forms.NumberInput(attrs={'class': 'form-control form-control-lg text-center', 'min': '0'}),
        }


from django import forms
from .models import PigeonPair

class PigeonPairForm(forms.ModelForm):
    class Meta:
        model = PigeonPair
        fields = ['pair_code', 'breed', 'loft_or_room', 'male_details', 'female_details', 'notes', 'image']
        widgets = {
            'pair_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'كود القص (مثال: A-101)'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'النوع / السلالة (مثال: زاجل، كشك، زاجل أبيض)'}),
            'loft_or_room': forms.Select(attrs={'class': 'form-select'}),
            'male_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'تفاصيل الذكر (اللون، مواصفاته، أو سبب التبديل)'}),
            'female_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'تفاصيل النتاية (اللون، مواصفاتها، أو سبب التبديل)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'ملاحظات إضافية عن القص'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }