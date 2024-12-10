from django import forms

from kursov_proekt.product.choices import ColorChoice, BrandChoice
from kursov_proekt.product.models import Product, Category, ProductSize


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

    xs_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    s_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    m_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    l_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    xl_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)

    size_36_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_37_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_38_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_39_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_40_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_41_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    size_42_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)

    def save(self, commit=True):
        product = super(BaseProduct, self).save(commit=False)

        if commit:
            product.save()

            # Изчисляваме общото количество от размерите
            total_quantity = 0

            if self.instance.category.name.lower() == 'clothing':
                sizes = ['XS', 'S', 'M', 'L', 'XL']
                for size in sizes:
                    quantity_field = f"{size.lower()}_quantity"
                    quantity = self.cleaned_data.get(quantity_field, 0)

                    # Проверяваме дали quantity е валидно число
                    if not isinstance(quantity, int):
                        quantity = 0  # Ако quantity не е цяло число, го задаваме на 0

                    total_quantity += quantity  # Добавяме количеството за съответния размер

                    # Ако количеството е повече от 0, създаваме записа за размер
                    if quantity > 0:
                        ProductSize.objects.create(product=product, size=size, stock_quantity=quantity)
                    if quantity <= 0:
                        quantity = 0
                        ProductSize.objects.create(product=product, size=size, stock_quantity=quantity)


            elif self.instance.category.name.lower() == 'shoes':
                sizes = ['36', '37', '38', '39', '40', '41', '42']
                for size in sizes:
                    quantity_field = f"size_{size}_quantity"
                    quantity = self.cleaned_data.get(quantity_field, 0)

                    # Проверяваме дали quantity е валидно число
                    if not isinstance(quantity, int):
                        quantity = 0  # Ако quantity не е цяло число, го задаваме на 0

                    total_quantity += quantity  # Добавяме количеството за съответния размер

                    # Ако количеството е повече от 0, създаваме записа за размер
                    if quantity > 0:
                        ProductSize.objects.create(product=product, size=size, stock_quantity=quantity)
                    if quantity <= 0:
                        quantity = 0
                        ProductSize.objects.create(product=product, size=size, stock_quantity=quantity)

            # Записваме общото количество в продукта, ако е необходимо
            # Ако не искаш да записваш общото количество в продукта, можеш да го пропуснеш
            product.save()

        return product


class SearchForm(forms.Form):
    search_data = forms.CharField(
        label='',
        required=False,
        max_length=10,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search...',
            }

        )
    )

class CreateProduct(BaseProduct):
    pass


class UpdateProduct(BaseProduct):
    pass
