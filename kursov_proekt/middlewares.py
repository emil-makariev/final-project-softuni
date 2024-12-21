from django.template.response import TemplateResponse

from kursov_proekt.orders.models import Orders


class ContextModification:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_template_response(request, response)

    def process_template_response(self, request, response):
        # Ensure the response is a TemplateResponse before attempting to modify context_data
        if isinstance(response, TemplateResponse):
            # Initialize 'context_data' if it is None
            if response.context_data is None:
                response.context_data = {}

            # Now safely add to the context_data
            response.context_data['user_logged_in'] = request.user.is_authenticated

            # Get group permissions and check for 'can_create_products' permission
            permissions = request.user.get_group_permissions()
            response.context_data['has_perm'] = 'product.can_create_products' in permissions

            valid_orders = Orders.objects.filter(status=False, profile_id=request.user.id)
            response.context_data['has_active_orders'] = valid_orders.exists()
            # Check if the user has any active (incomplete) orders
        return response

