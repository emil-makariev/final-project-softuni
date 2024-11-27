from django import forms

from kursov_proekt.product.choices import ColorChoice, BrandChoice, SizeChoice
from kursov_proekt.product.models import Product, Category


class BaseProduct(forms.ModelForm):
    # CATEGORY_CHOICES = [(category.id, category.name) for category in Category.objects.all()]

    class Meta:
        model = Product
        fields = '__all__'


    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    discount_price = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    size = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        choices=SizeChoice
    )
    color = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        choices=ColorChoice
    )

    main_image = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    sku = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    stock_quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        queryset=Category.objects.all()
    )
    brand = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),choices=BrandChoice

    )



class CreateProduct(BaseProduct):
    pass


class UpdateProduct(BaseProduct):
    pass
