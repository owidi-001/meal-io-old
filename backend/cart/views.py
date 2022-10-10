# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Location
# from .schema import OrderSchema
from .serializers import CartItemSerializer, CartSerializer
from product.models import Product


class OrderView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        orders = Cart.objects.all()
        # print(orders)
        serializer = CartSerializer(orders, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        data["user"] = request.user.id

        serializer = CartSerializer(data=data)
        # print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        # print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        data = request.data
        order = get_object_or_404(Cart, id=data["order"])

        # Check if data has location
        if data["location"]:
            lng = data["location"]["lng"]
            lat = data["location"]["lat"]
            name = data["location"]["name"]
            city = data["location"]["city"]
            street = data["location"]["street"]

            location = Location.objects.update_or_create(lng=lng, lat=lat, name=name, city=city, street=street)

            # The above returns a tuple of two, the object and bool if created
            # print(location)

            if location:
                order.location = location[0]
            else:
                print(location)

        if order:
            order.status = data["status"]
            order.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        order = get_object_or_404(Cart, id=data["order"])

        if order:
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderItemView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        items = CartItem.objects.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        cart = get_object_or_404(Cart, id=data["cart"])
        product = get_object_or_404(Product, id=data["product"])
        quantity = data["quantity"]
        item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)

        try:
            item.save()
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        item = get_object_or_404(CartItem, id=data["item"])

        if item:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)