from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import TokenAuthentication


class QueryParamAuthentication(TokenAuthentication):
    query_param_name = 'token'

    def authenticate(self, request):
        token = request.query_params.get(self.query_param_name)
        if token:
            return self.authenticate_credentials(token)
        return super().authenticate(request)


class NoCSRFSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
