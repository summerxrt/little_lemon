from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register the GroupViewSet
router = DefaultRouter()
router.register(r'groups/manager/users', views.GroupViewSet, basename='group-manager-users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('reservation/menu/', views.menu_view, name='menu'),
    path('', views.index_view, name='index'),  # Ensure this line points to index_view
    path('categories/', views.CategoriesView.as_view(), name='categories'),
    path('menu-items/', views.MenuItemListView.as_view(), name='menu-items'),
    path('menu-items/category/', views.CategoriesView.as_view(), name='menu-items-category'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('groups/managers/users/', views.ManagersListView.as_view(), name='manager-user-list'),
    path('groups/delivery-crew/users/', views.DeliveryCrewListView.as_view(), name='delivery-crew-users'),
    path('groups/delivery-crew/users/<int:pk>/', views.DeliveryCrewRemoveView.as_view(), name='delivery-crew-user-detail'),
    path('cart/menu-items/', views.CartOperationsView.as_view(), name='cart-menu-items'),
    path('orders/', views.OrderOperationsView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.SingleOrderView.as_view(), name='order-detail'),
    path('book/', views.book, name='book'),
    path('bookings/', views.bookings, name='bookings'),

    # Include router-generated URLs
    path('', include(router.urls)),
]