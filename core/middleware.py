import traceback
import logging
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

class ExceptionHandlingMiddleware:
    """
    Middleware to handle exceptions and provide meaningful error messages
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        # Log the error
        logger.error(f"Unhandled exception: {str(exception)}")
        logger.error(traceback.format_exc())
        
        # Check if it's an AJAX/API request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/api/'):
            return JsonResponse({
                'status': 'error',
                'message': str(exception) if str(exception) else 'An unexpected error occurred'
            }, status=500)
        
        # For regular requests, render the 500 error page
        return render(request, '500.html', {
            'error_message': str(exception) if str(exception) else 'An unexpected error occurred'
        }, status=500)
