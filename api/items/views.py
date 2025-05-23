from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .service import WildberriesParser


class ProductsAPIView(APIView):
    @staticmethod
    def get(request):
        query = request.query_params.get('query', '')
        color = request.query_params.get('color')
        price_from = request.query_params.get('price_from')
        price_to = request.query_params.get('price_to')

        if not query:
            return Response(
                {'error': 'query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            price_from = float(price_from) if price_from else None
            price_to = float(price_to) if price_to else None

            total, products = WildberriesParser(query).get_products(
                color=color,
                price_from=price_from,
                price_to=price_to
            )
        except Exception as e:
            return Response({'error': str(e)})

        return Response({
            "total": total,
            "products": products,
        })
