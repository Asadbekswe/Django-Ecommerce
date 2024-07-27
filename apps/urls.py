from django.urls import path

from apps.views import ProductListView, ProductDetailView, CustomLoginView, CustomLogoutView, CustomRegisterView, \
    CustomSettingsView, AddToCartView, CartListView, CartItemDeleteView, FavouriteView, \
    CheckoutView, AddressUpdateView, AddressCreateView, OrderListView, OrderDeleteView, \
    OrderDetailView, CustomOrderListView, CustomerOrderCreateView, CustomOrderDetailView, ProductGridView, \
    CustomerGetProView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list_page'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product-grid', ProductGridView.as_view(), name='product_grid'),
    path('login', CustomLoginView.as_view(), name='login_page'),
    path('logout', CustomLogoutView.as_view(), name='logout_page'),
    path('register', CustomRegisterView.as_view(), name='register_page'),
    path('settings', CustomSettingsView.as_view(), name='settings_page'),
    path('shopping-cart', CartListView.as_view(), name='shopping_cart_page'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add_cart_page'),
    path('remove-cart/<int:pk>/', CartItemDeleteView.as_view(), name='delete_cart_item'),
    path('favorite/<int:pk>', FavouriteView.as_view(), name='favorite_page'),
    path('checkout', CheckoutView.as_view(), name='checkout_page'),
    path('update-address/<int:pk>', AddressUpdateView.as_view(), name='update_address'),
    path('create-address', AddressCreateView.as_view(), name='create_address'),
    path('orders', OrderListView.as_view(), name='orders_list'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('custom-order-create', CustomerOrderCreateView.as_view(), name='create_order'),
    path('custom-get-pro', CustomerGetProView.as_view(), name='custom_get_pro'),
    path('order/delete/<int:pk>', OrderDeleteView.as_view(), name='order_delete'),
    path('custom-order-list', CustomOrderListView.as_view(), name="custom_order_list"),
    path('custom-order-detail/<int:pk>', CustomOrderDetailView.as_view(), name='custom_order_detail')
]
