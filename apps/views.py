from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import F, Sum, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView, FormView

from apps.forms import UserRegisterModelForm, ReviewForm, AddressForm, OrderCreateModelForm, RecaptchaForm
from apps.models import CreditCard, Order, SiteSettings, OrderItem
from apps.models.products import Product, Category, CartItem, Favorite, User
from apps.models.user import Address
from apps.tasks import send_to_email


class CategoryMixin:
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(CategoryMixin, ListView):
    queryset = Product.objects.order_by('-created_at')
    template_name = 'apps/product/product-list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(long_description__icontains=search_query)
            )
        return qs


class ProductGridView(CategoryMixin, ListView):
    queryset = Product.objects.all()
    template_name = 'apps/product/product-grid.html'
    context_object_name = 'products'
    paginate_by = 10


class ProductDetailView(CategoryMixin, DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'


class ProductReviewView(DetailView):
    model = Product
    template_name = 'apps/product/product-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        reviews = product.reviews.all()
        review_form = ReviewForm()

        context['reviews'] = reviews
        context['review_form'] = review_form
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.save()
            return redirect('product_detail', pk=product.pk)
        return self.render_to_response(self.get_context_data(review_form=review_form))


class CustomRegisterView(CreateView):
    template_name = 'apps/auth/register.html'
    form_class = UserRegisterModelForm
    success_url = reverse_lazy('product_list_page')
    redirect_authenticated_user = True

    def form_valid(self, form):
        form.save()
        # send_to_email('Your account has been created!', form.data['email'])
        send_to_email.delay('Your account has been created!', form.data['email'])
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = reverse_lazy('product_list_page')
            if redirect_to == self.request.path:
                raise ValueError()
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView, FormView):
    template_name = 'apps/auth/login.html'
    next_page = reverse_lazy('product_list_page')
    redirect_authenticated_user = True
    form_class = RecaptchaForm


class CustomLogoutView(LoginRequiredMixin, View):
    template_name = 'apps/auth/login.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('product_list_page')


class CustomSettingsView(LoginRequiredMixin, CategoryMixin, UpdateView):
    queryset = User.objects.all()
    fields = 'first_name', 'last_name'
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')

    def get_object(self, queryset=None):
        return self.request.user


class FavouriteView(LoginRequiredMixin, CategoryMixin, View):
    template_name = 'apps/shop/favourite.html'

    def get(self, request, pk, *args, **kwargs):
        obj, created = Favorite.objects.get_or_create(user=request.user, product_id=pk)
        if not created:
            obj.delete()
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('product_detail', pk=pk)


class CartListView(CategoryMixin, ListView):
    queryset = CartItem.objects.all()
    template_name = 'apps/shopping/shopping_cart.html'
    context_object_name = 'cart_items'
    success_url = reverse_lazy('shopping_cart_page')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        qs = self.get_queryset()

        ctx.update(
            **qs.aggregate(
                total_sum=Sum(F('quantity') * F('product__price') * (100 - F('product__discount_percent')) / 100),
                total_count=Sum(F('quantity'))
            )
        )
        return ctx


class AddToCartView(LoginRequiredMixin, CreateView):
    model = CartItem

    def get_success_url(self):
        return reverse_lazy('shopping_cart_page')

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        product = get_object_or_404(Product, id=pk)

        cart_item, created = CartItem.objects.get_or_create(user=self.request.user, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect(self.get_success_url())


class CartItemDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('shopping_cart_page')

    def get(self, request, pk, *args, **kwargs):
        cart_item = CartItem.objects.filter(user=self.request.user, pk=pk).first()
        if cart_item:
            cart_item.delete()
        return redirect(self.success_url)


class CheckoutView(LoginRequiredMixin, CategoryMixin, ListView):
    queryset = CartItem.objects.all()
    template_name = 'apps/shopping/checkout.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        credit_cart = CreditCard.objects.filter(owner=self.request.user)
        addresses = Address.objects.filter(user=self.request.user)
        sitesettings = SiteSettings.objects.first()

        cart_items = self.get_queryset()

        subtotal = cart_items.aggregate(
            subtotal=Sum((F('quantity') * F('product__price') * (100 - F('product__discount_percent')) / 100))
        )['subtotal'] or 0

        shipping_cost = cart_items.aggregate(
            shipping_cost=Sum(F('product__shipping_cost'))
        )['shipping_cost'] or 0

        total = subtotal + shipping_cost  # your coupon   - coupon_discount
        scot = (total * sitesettings.tax) // 100
        total += scot

        context.update({
            'credit_cards': credit_cart,
            'addresses': addresses,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'total': total,
            'tax': sitesettings.tax,
            'scot': scot
        })
        return context


class AddressCreateView(CategoryMixin, CreateView):
    model = Address
    template_name = 'apps/address/create_address.html'
    form_class = AddressForm
    success_url = reverse_lazy('checkout_page')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, CategoryMixin, UpdateView):
    model = Address
    template_name = 'apps/address/update_address.html'
    fields = ('city', 'street', 'zip_code', 'phone')
    success_url = reverse_lazy('checkout_page')


class CustomerOrderCreateView(LoginRequiredMixin, CategoryMixin, CreateView):
    model = Order
    template_name = 'apps/customer/customer_order_list.html'
    form_class = OrderCreateModelForm
    success_url = reverse_lazy('custom_order_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CustomOrderListView(CategoryMixin, ListView):
    model = Order
    template_name = 'apps/customer/customer_order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class CustomOrderDetailView(CategoryMixin, DetailView):
    model = Order
    template_name = 'apps/customer/customer_order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        qs = OrderItem.objects.filter(order_id=context['order'].id)

        context.update(
            **qs.aggregate(
                subtotal=Sum(F('quantity') * (F('product__price') * (
                        100 - F('product__discount_percent')) / 100)),
                shipping_cost=Sum(F('product__shipping_cost'))
            )
        )

        context['tax'] = SiteSettings.objects.first().tax
        return context


class CustomerGetProView(CategoryMixin, TemplateView):
    template_name = 'apps/customer/customer_getpro.html'


class OrderListView(CategoryMixin, ListView):  # ADMIN
    model = Order
    template_name = 'apps/orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class OrderDetailView(CategoryMixin, DetailView):  # ADMIN
    model = Order
    template_name = 'apps/customer/customer_order_detail.html'
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class OrderDeleteView(DeleteView):  # admin
    model = Order
    success_url = reverse_lazy('orders_list')


def error_404(request, exception):
    return render(request, 'apps/parts/404.html', status=404)


def error_500(request):
    return render(request, 'apps/parts/500.html', status=500)
