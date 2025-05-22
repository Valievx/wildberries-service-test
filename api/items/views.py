import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ProductsAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        color_filter = request.query_params.get('color', '').lower()
        price_from = request.query_params.get('price_from')
        price_to = request.query_params.get('price_to')

        if not query:
            return Response({'error': 'query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://search.wb.ru/exactmatch/ru/common/v13/search"
        params = {
            'dest': '123585853',
            'query': query,
            'resultset': 'catalog',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Request failed: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if response.status_code != 200:
            return Response({'error': 'Failed to fetch data from Wildberries'}, status=response.status_code)

        data = response.json()
        products = data.get('data', {}).get('products', [])

        if color_filter:
            products = [
                p for p in products
                if any(color_filter in c.get('name', '').lower() for c in p.get('colors', []))
            ]

        filtered_products = []
        for product in products:
            prices = [
                size.get('price', {}).get('total', 0)
                for size in product.get('sizes', [])
                if isinstance(size.get('price', {}).get('total', None), int)
            ]

            if not prices:
                continue

            min_price = min(prices)

            if price_from:
                try:
                    price_from_val = int(float(price_from) * 100)
                    if min_price < price_from_val:
                        continue
                except ValueError:
                    return Response({'error': 'Invalid price_from value'}, status=status.HTTP_400_BAD_REQUEST)

            if price_to:
                try:
                    price_to_val = int(float(price_to) * 100)
                    if min_price > price_to_val:
                        continue
                except ValueError:
                    return Response({'error': 'Invalid price_to value'}, status=status.HTTP_400_BAD_REQUEST)

            filtered_products.append(product)

        return Response(filtered_products)
