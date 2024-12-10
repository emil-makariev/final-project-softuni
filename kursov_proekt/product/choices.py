from django.db import models


class SizeChoiceClothes(models.TextChoices):
    XS = "XS", "XS"
    S = "S", "S"
    M = "M", "M"
    L = "L", "L"
    XL = "XL", "XL"

class SizeChoiceShoes(models.TextChoices):

        thirty_six = '36', '36'
        thirty_seven= '37', '37'
        thirty_eight= '38', '38'
        thirty_nine= '39', '39'
        forty= '40', '40'


class ColorChoice(models.TextChoices):
    RED = "red", "Red"
    BLUE = "blue", "Blue"
    YELLOW = "yellow", "Yellow"
    BLACK = "black", "Black"
    WHITE = "white", "White"
    PINK = "pink", "Pink"
    LIGHT_PURPLE = "light-purple", "Light-Purple"
    GREY = "grey", "Grey"
    BROWN = "brown", "Brown"


class BrandChoice(models.TextChoices):
    LOUIS_VUITTON = "LV", "Louis Vuitton"
    HERMES = "Hermes", "Hermes"
    GUCCI = "Gucci", "Gucci"
    CHANEL = "Chanel", "Chanel"