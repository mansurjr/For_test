from django.http import HttpResponseForbidden

class RestrictAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/super-secret-admin/"):
            allowed_ips = ["127.0.0.1", "192.168.1.100"]
            if request.META.get("REMOTE_ADDR") not in allowed_ips:
                return HttpResponseForbidden("Access Denied, You are not allowed to access this page.") 
        return self.get_response(request)
