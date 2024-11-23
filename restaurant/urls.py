from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register the GroupViewSet
router = DefaultRouter()
router.register(r'groups/manager/users', views.GroupViewSet, basename='group-manager-users')


urlpatterns = [
    # Authentication endpoints
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    # Application endpoints
    path('', views.index_view, name='home'),  # Homepage
    path('about/', views.about_view, name='about'),  # About Page
    path('menu/', views.menu_view, name='menu'),  # Menu Page
    path('reservations/', views.book, name='reservations'),  # Reservations (book a table)
    path('bookings/', views.bookings, name='bookings'),  # View all bookings
    path('book/', views.book, name='book'),

    # Menu items
    path('menu-items/', views.MenuItemListView.as_view(), name='menu-items'),
    path('menu-items/category/', views.CategoriesView.as_view(), name='menu-items-category'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),

    # User and Group management
    path('groups/managers/users/', views.ManagersListView.as_view(), name='manager-user-list'),
    path('groups/delivery-crew/users/', views.DeliveryCrewListView.as_view(), name='delivery-crew-users'),
    path('groups/delivery-crew/users/<int:pk>/', views.DeliveryCrewRemoveView.as_view(), name='delivery-crew-user-detail'),

    # Cart operations
    path('cart/menu-items/', views.CartOperationsView.as_view(), name='cart-menu-items'),

    # Order operations
    path('orders/', views.OrderOperationsView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.SingleOrderView.as_view(), name='order-detail'),

    # Include router-generated URLs
    path('', include(router.urls)),
]
