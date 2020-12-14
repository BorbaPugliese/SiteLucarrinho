from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import reverse
from django.db.models.signals import post_save


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    price1 = models.FloatField(default=0)
    price2 = models.FloatField(default=0)
    price3 = models.FloatField(default=0)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
    def get_mean_price(self):
        return (self.price1 * self.price2 * self.price3)/3

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price1(self):
        return self.quantity * self.item.price1

    def get_total_item_price2(self):
        return self.quantity * self.item.price2

    def get_total_item_price3(self):
        return self.quantity * self.item.price3

    def get_total_item_price(self):
        total1 = self.get_total_item_price1()
        total2 = self.get_total_item_price2()
        total3 = self.get_total_item_price3()
        return min(total1, total2, total3)

    def get_final_price1(self):
        return self.get_total_item_price1()

    def get_final_price2(self):
        return self.get_total_item_price2()

    def get_final_price3(self):
        return self.get_total_item_price3()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    envio_option = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total1 = self.get_total1()
        total2 = self.get_total2()
        total3 = self.get_total3()
        return min(total1, total2, total3)

    def get_best_market(self):
        total1 = self.get_total1()
        total2 = self.get_total2()
        total3 = self.get_total3()
        best = min(total1, total2, total3)
        if best == total3:
            return "Supermercado 3"
        elif best == total2:
            return 'Supermercado 2'
        else:
            return 'Supermercado 1'


    def get_total1(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price1()
        return total

    def get_total2(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price2()
        return total

    def get_total3(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price3()
        return total


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)



post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)