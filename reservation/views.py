from rest_framework import generics, viewsets
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.views import View
from .models import MenuItem, Cart, Order, OrderItem, Category, Booking
from .serializers import (
    MenuItemSerializer, ManagerListSerializer, CartSerializer,
    OrderSerializer, CartAddSerializer, OrderPutSerializer, CategorySerializer, DeliveryCrewListSerializer, SingleOrderSerializer
)
from .paginations import MenuItemListPagination
from django.contrib.auth.models import Group, User
from .permissions import IsManager, IsDeliveryCrew
import math
from datetime import date, datetime
from .forms import BookingForm
from django.core import serializers
from .permissions import IsManager, IsDeliveryCrew

# Root API view for a welcome message and endpoint guide
class ApiRootView(View):
    def get(self, request):
        return JsonResponse({
            "message": "Welcome to the Little Lemon API!",
            "available_endpoints": {
                "menu_items": "/api/menu-items/",
                "categories": "/api/menu-items/category/",
                "managers": "/api/groups/managers/users/",
                "delivery_crew": "/api/groups/delivery-crew/users/",
                "cart": "/api/cart/menu-items/",
                "orders": "/api/orders/"
            }
        })

# View to manage list and creation of menu items
class MenuItemListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', 'category']
    pagination_class = MenuItemListPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

# View to manage list and creation of categories
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

# View to retrieve, update, or delete a specific menu item
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method in ['PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
        menuitem = get_object_or_404(MenuItem, pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return JsonResponse(status=200, data={'message': f'Featured status of {menuitem.title} changed to {menuitem.featured}'})

# ViewSet for managing users in Manager and Delivery Crew groups
class GroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        users = User.objects.filter(groups__name='Managers')
        items = ManagerListSerializer(users, many=True)
        return Response(items.data, status=status.HTTP_200_OK)

    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Managers")
        managers.user_set.add(user)
        return Response({"message": "User added to the manager group"}, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Managers")
        managers.user_set.remove(user)
        return Response({"message": "User removed from the manager group"}, status=status.HTTP_200_OK)

# Corrected CartOperationsView for managing cart items
class CartOperationsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return Cart.objects.filter(user=self.request.user).order_by('id')

    def post(self, request, *arg, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        item_id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=item_id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(
                user=request.user, quantity=quantity,
                unit_price=item.price, price=price, menuitem_id=item_id
            )
        except:
            return JsonResponse(status=409, data={'message': 'Item already in cart'})

        return JsonResponse(status=201, data={'message': 'Item added to cart!'})

class ManagersListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Managers')
            managers.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Managers group'})

class DeliveryCrewListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='DeliveryCrew')
    serializer_class = DeliveryCrewListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='DeliveryCrew')
            delivery_crew.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Delivery Crew group'})

class DeliveryCrewRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        delivery_crew = Group.objects.get(name='DeliveryCrew')
        delivery_crew.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User removed from Delivery Crew group'})

class OrderOperationsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Order.objects.all()
    serializer_class = SingleOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

# Function to handle booking form submission
def book(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Booking successful!"})
        else:
            return HttpResponseBadRequest("Invalid data")
    else:
        form = BookingForm()
    return render(request, "book.html", {"form": form})

# Function to handle displaying bookings
def bookings(request):
    if request.method == "GET":
        bookings = Booking.objects.all()
        booking_json = serializers.serialize('json', bookings)
        return JsonResponse(booking_json, safe=False)  # Respond with JSON so that the JavaScript can consume it
    else:
        return HttpResponseBadRequest("Invalid request method")

# Add the menu_view function
def menu_view(request):
    # Your view logic here
    return render(request, 'menu.html')