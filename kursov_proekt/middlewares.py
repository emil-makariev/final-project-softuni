from django.utils.deprecation import MiddlewareMixin


class ContextModification(MiddlewareMixin):

    def process_template_response(self, request, response):

        if hasattr(response, 'context_data'):
            response.context_data['user_logged_in'] = request.user.is_authenticated
            permissions = request.user.get_group_permissions()
            response.context_data['has_perm'] = True if 'product.can_create_products' in permissions else False
        return response
