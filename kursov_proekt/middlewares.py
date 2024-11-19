from django.utils.deprecation import MiddlewareMixin


class ContextModification(MiddlewareMixin):

    def process_template_response(self, request, response):

        if hasattr(response, 'context_data'):
            response.context_data['user_logged_in'] = request.user.is_authenticated

        return response
