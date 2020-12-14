import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm
from .models import Item, OrderItem, Order, UserProfile



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                envio_option = form.cleaned_data.get('envio_option')

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                    order.totalprice += Order.get_total(order)

                order.User = userprofile
                order.ordered = True
                order.ref_code = create_ref_code()

                if envio_option == 'W':
                    order.envio_option = 'Whatsapp'
                    order.save()
                    messages.success(self.request, "Seu envio foi feito com sucesso!")
                    return redirect("/")
                elif envio_option == 'E':
                    order.envio_option = 'Email'
                    order.save()
                    messages.success(self.request, "Seu envio foi feito com sucesso!")
                    return redirect("/")
                else:
                    messages.warning(
                        self.request, "Opção de envio inválida")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "Você não tem um pedido ativo")
            return redirect("core:order-summary")

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"




class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Você não tem um pedido ativo")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "A quantidade do item foi atualizada")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "O item foi adicionado ao carrinho")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "O item foi adicionado ao carrinho")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "Item removido do carrinho")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Esse item não está no carrinho")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Você não tem um pedido ativo")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Quantidade do Item atualizada")
            return redirect("core:order-summary")
        else:
            messages.info(request, "O item não está no seu carrinho")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Você não tem um pedido ativo")
        return redirect("core:product", slug=slug)

