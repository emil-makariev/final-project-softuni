from django.db import models


class SizeChoice(models.TextChoices):
    XS = "XS", "XS"
    S = "S", "S"
    M = "M", "M"
    L = "L", "L"
    XL = "XL", "XL"


class ColorChoice(models.TextChoices):
    RED = "Red", "Red"
    BLUE = "Blue", "Blue"
    YELLOW = "Yellow", "Yellow"
    BLACK = "Black", "Black"
    WHITE = "White", "White"
    PINK = "Pink", "Pink"
    LIGHT_PURPLE = "Light-Purple", "Light-Purple"
    GREY = "Grey", "Grey"
    BROWN = "BROWN", "BROWN"


class BrandChoice(models.TextChoices):
    LOUIS_VUITTON = "LV", "Louis Vuitton"
    HERMES = "Hermes", "Hermes"
    GUCCI = "Gucci", "Gucci"
    CHANEL = "Chanel", "Chanel"