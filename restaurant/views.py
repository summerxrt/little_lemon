from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import MenuItem, Cart, Order, OrderItem, Category, Booking, Menu
from .forms import BookingForm
from .serializers import (
    MenuItemSerializer, ManagerListSerializer, CartSerializer,
    OrderSerializer, CartAddSerializer, OrderPutSerializer,
    CategorySerializer, DeliveryCrewListSerializer, SingleOrderSerializer
)
from .permissions import IsManager, IsDeliveryCrew
from .paginations import MenuItemListPagination
from django.core import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
import json
from .models import Booking
from django.views.decorators.csrf import csrf_exempt

# Basic views
def index_view(request):
    return render(request, 'index.html')

def about_view(request):
    return render(request, 'about.html')

def menu_view(request):
    menu_items = Menu.objects.all()
    return render(request, 'menu.html', {'menu_items': menu_items})

# Booking views
@csrf_exempt
def book(request):
    # Define the available reservation hours (10:00 AM to 8:00 PM)
    hours = [f"{i:02d}:00" for i in range(10, 21)]  

    if request.method == "POST":
        try:
            if request.headers.get('Content-Type') == 'application/json':
                # Parse JSON body if the content type is application/json
                data = json.loads(request.body)
            else:
                # Otherwise, it's a form submission, use request.POST
                data = request.POST

            print("Received data:", data)  # Log the received data for debugging

            # Create a BookingForm instance using the parsed data
            form = BookingForm(data)
            print("Form data:", form.data)  # Log the form data for debugging

            # Validate the form
            if form.is_valid():
                form.save()  # Save the form to create a Booking object
                return JsonResponse({"message": "Booking successful!"}, status=200)
            else:
                # Collect form errors if the form is not valid
                print("Form errors:", form.errors)  # Log form errors for debugging
                return JsonResponse({"errors": form.errors}, status=400)

        except json.JSONDecodeError as e:
            print("JSON decode error:", e)  # Log JSON decode errors
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            print("General error:", e)  # Log any other errors
            return JsonResponse({"error": str(e)}, status=500)

    # If it's a GET request, render the booking form with available hours
    return render(request, "book.html", {"hours": hours})

def bookings(request):
    if request.method == "GET":
        bookings = Booking.objects.all()
        return render(request, "bookings.html", {"bookings": bookings})
    else:
        return HttpResponseBadRequest("Invalid request method")
# DRF API views
class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemListPagination
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class ManagersListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerListSerializer

class DeliveryCrewListView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='DeliveryCrew')
    serializer_class = DeliveryCrewListSerializer

class OrderOperationsView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = SingleOrderSerializer

# Group management
class GroupViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    
    def list(self, request):
        users = User.objects.filter(groups__name='Managers')
        return Response(ManagerListSerializer(users, many=True).data)

# Cart operations
class CartOperationsView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class DeliveryCrewRemoveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk, groups__name='DeliveryCrew')
        user.groups.clear()  # Remove user from all groups
        user.delete()  # Delete the user
        return Response(status=status.HTTP_204_NO_CONTENT)

# User registration
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})