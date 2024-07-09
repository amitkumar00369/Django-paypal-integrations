# paypal_integration/views.py
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import json
from .models import Payment
from .serializers import PaymentSerializer

def generate_access_token():
    try:
        response = requests.post(
            f"{settings.PAYPAL_URL}/v1/oauth2/token",
            data={'grant_type': 'client_credentials'},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        return response.json()['access_token']
    except requests.RequestException as e:
        print(f"Error generating access token: {e}")
        raise Exception('Failed to generate access token')

class create_order(APIView):
    def post(self, request):
        try:
            access_token = generate_access_token()

            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "items": [{
                        "name": 'Buy products Paypal integrations',
                        "description": 'for future projects so we learn paypal integrations',
                        "quantity": 1,
                        "unit_amount": {
                            "currency_code": 'USD',
                            "value": 100
                        }
                    }],
                    "amount": {
                        "currency_code": 'USD',
                        "value": 100,
                        "breakdown": {
                            "item_total": {
                                "currency_code": 'USD',
                                "value": 100
                            }
                        }
                    }
                }],
                "application_context": {
                    "return_url": f"{settings.BASE_URL}complete-order",
                    "cancel_url": f"{settings.BASE_URL}cancel-order",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "PAY_NOW",
                    "brand_name": "amit.i0"
                }
            }

            response = requests.post(
                f"{settings.PAYPAL_URL}/v2/checkout/orders",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                },
                json=payload
            )
            response.raise_for_status()
            approval_url = next(link['href'] for link in response.json()['links'] if link['rel'] == 'approve')

            return Response({'link': approval_url, 'code': 200}, status=200)

        except Exception as e:
            print(f"Error creating order: {e}")
            return Response({'message': 'An error occurred while creating the order', 'code': 500}, status=500)

class capture_order(APIView):
    def post(self, request):
        try:
            access_token = generate_access_token()
            data = json.loads(request.body)
            order_id = data.get('orderId')

            response = requests.post(
                f"{settings.PAYPAL_URL}/v2/checkout/orders/{order_id}/capture",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {access_token}'
                }
            )
            response.raise_for_status()
            return Response(response.json(), status=200)
        except Exception as e:
            print(f"Error capturing order: {e}")
            return Response({'message': 'An error occurred while capturing the order', 'code': 500}, status=500)


# class complete_order(APIView):
#     def get(self,request):
#         try:
#             capture=capture_order()
#         except Exception as e:
#             print(f"Error capturing order: {e}")
#             return Response({'message': 'An error occurred while capturing the order', 'code': 500}, status=500)
class complete_order(APIView):
    def get(self,request):

        try:
            access_token = generate_access_token()
            token = request.GET.get('token')

            response = requests.post(
            f"{settings.PAYPAL_URL}/v2/checkout/orders/{token}/capture",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            )
            response.raise_for_status()
            capture_result = response.json()

            if not capture_result:
                return JsonResponse({'message': 'Payment not captured', 'code': 400}, status=400)

            existing_payment = Payment.objects.filter(payment_id=capture_result['id']).first()
            if existing_payment:
                return JsonResponse({'message': 'Payment ID already exists', 'code': 409}, status=409)

            payment_details = Payment.objects.create(
            payment_id=capture_result['id'],
            status=capture_result['status'],
            email=capture_result['payment_source']['paypal']['email_address'],
            account_id=capture_result['payment_source']['paypal']['account_id'],
            account_status=capture_result['payment_source']['paypal']['account_status'],
            payer_id=capture_result['payer']['payer_id'],
            first_name=capture_result['payer']['name']['given_name'],
            last_name=capture_result['payer']['name']['surname'],
            payment_country_code=capture_result['payer']['address']['country_code']
            )
            print(payment_details)
            serializer=PaymentSerializer(payment_details)
        

            return JsonResponse({'message': 'Successful payment by user', 'data': serializer.data, 'code': 200}, status=200)

        except Exception as e:
            print(f"Error completing order: {e}")
            return JsonResponse({'message': 'Internal server error', 'error': str(e)}, status=500)

# def cancel_order(request):
#     return redirect('/')