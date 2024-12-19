from attr.filters import exclude
from django import forms

from kursov_proekt.product.choices import ColorChoice, BrandChoice
from kursov_proekt.product.models import Product, Category, ProductSize, Accessory


class BaseProduct(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'  # Включва всички полета
        exclude = ['num_of_times_purchased']

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    price = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    discount_price = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    color = forms.ChoiceField(
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        choices=ColorChoice.choices
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
        ),choices=BrandChoice.choices

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

    accessory_quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)

    def save(self, commit=True):
        product = super(BaseProduct, self).save(commit=False)

        if commit:
            product.save()

            # Изчисляваме общото количество от размерите
            total_quantity = 0

            if self.instance.category.name.lower() == 'accessories':
                self.instance.is_active = True
                # Добавяме само едно поле за общото количество на аксесоарите
                accessory_quantity = self.cleaned_data.get('accessory_quantity', 0)
                total_quantity += accessory_quantity  # Добавяме количеството на аксесоара
                if accessory_quantity > 0:
                    # Създаване на аксесоар без размер
                    Accessory.objects.create(product=product, stock_quantity=accessory_quantity)

            if self.instance.category.name.lower() == 'clothing':
                self.instance.is_active = True

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
                self.instance.is_active = True

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


class EditProductForm(BaseProduct):
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['num_of_times_purchased']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ако имаме продукт с определена категория, зареждаме количествата
        if self.instance.pk:  # Проверяваме дали имаме инстанция на продукта (за редактиране)
            if self.instance.category.name.lower() == 'clothing':
                sizes = ['XS', 'S', 'M', 'L', 'XL']
                for size in sizes:
                    field_name = f'{size.lower()}_quantity'
                    self.fields[field_name] = forms.IntegerField(
                        widget=forms.NumberInput(attrs={'class': 'form-control'}),
                        required=False,
                        initial=self.get_size_quantity(size)
                    )
            elif self.instance.category.name.lower() == 'shoes':
                sizes = ['36', '37', '38', '39', '40', '41', '42']
                for size in sizes:
                    field_name = f'size_{size}_quantity'
                    self.fields[field_name] = forms.IntegerField(
                        widget=forms.NumberInput(attrs={'class': 'form-control'}),
                        required=False,
                        initial=self.get_size_quantity(size)
                    )
            elif self.instance.category.name.lower() == 'accessories':
                print('asas')
                self.fields['accessory_quantity'] = forms.IntegerField(
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=False,
                    initial=self.instance.accessory.stock_quantity
                )

    def get_size_quantity(self, size):
        # Връщаме съществуващото количество за конкретен размер от ProductSize
        try:
            return ProductSize.objects.get(product=self.instance, size=size).stock_quantity
        except ProductSize.DoesNotExist:
            print('o')
            return 0  # Ако няма запис за този размер, връщаме 0

    def save(self, commit=True):
        product = super().save(commit=False)

        # Ensure the product is active if not already
        if product.is_active == False:
            product.is_active = True

        if self.instance.pk:
            if self.instance.category.name.lower() == 'clothing':
                sizes = ['XS', 'S', 'M', 'L', 'XL']
                for size in sizes:
                    field_name = f'{size.lower()}_quantity'
                    quantity = self.cleaned_data.get(field_name)
                    if quantity is not None:
                        self.update_size_quantity(size, quantity)
            elif self.instance.category.name.lower() == 'shoes':
                sizes = ['36', '37', '38', '39', '40', '41', '42']
                for size in sizes:
                    field_name = f'size_{size}_quantity'
                    quantity = self.cleaned_data.get(field_name)
                    if quantity is not None:
                        self.update_size_quantity(size, quantity)
            elif self.instance.category.name.lower() == 'accessories':
                accessory_quantity = self.cleaned_data.get('accessory_quantity')
                if accessory_quantity is not None:
                    # Ensure accessory exists or create one if it doesn't
                    if not hasattr(self.instance, 'accessory'):
                        self.instance.accessory = Accessory.objects.create(product=self.instance)

                    self.update_accessory_quantity(accessory_quantity)

        if commit:
            product.save()

        return product

    def update_size_quantity(self, size, quantity):
        # Обновяваме или създаваме нов запис за размера
        try:
            product_size = ProductSize.objects.get(product=self.instance, size=size)
            product_size.stock_quantity = quantity

            if product_size.stock_quantity > product_size.max_size:
                product_size.max_size= quantity
            else:
                product_size.max_size += quantity
            product_size.save()
        except ProductSize.DoesNotExist:
            # Ако не съществува, създаваме нов запис
            ProductSize.objects.create(product=self.instance, size=size, stock_quantity=quantity)

    def update_accessory_quantity(self, quantity):
        # Обновяваме количеството за аксесоар
        accessory = self.instance.accessory
        accessory.stock_quantity = quantity
        if accessory.stock_quantity > accessory.max_quantity_accessory:
            accessory.max_quantity_accessory = quantity
        else:
            accessory.max_quantity_accessory += quantity

        # Извикваме save() за да запишем актуализираните стойности в базата данни
        accessory.save()
        self.instance.save()