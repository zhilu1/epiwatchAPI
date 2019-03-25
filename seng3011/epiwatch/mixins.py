import logging
from django.utils.timezone import now
from rest_framework import status
from epiwatch.log_middleware import RequestLogMiddleware
from django.utils.decorators import decorator_from_middleware
import socket
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class LoggingMixin(object):
    def finalize_response(self, request, response, *args, **kwargs):
        # regular finalize response
        response = super().finalize_response(request, response, *args, **kwargs)
        status_code = response.status_code
        cur_time = request.start_time.astimezone()
        log_kwargs = {
            'remote_address': request.META['REMOTE_ADDR'],
            'server_hostname': socket.gethostname(),
            'method': request.method,
            'status_code': status_code,
            'request_path': request.get_full_path(),
            'access_time': request.start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            'service_time': (datetime.now(timezone.utc) - request.start_time).total_seconds(),
            'service_provide': "NULL"
        }
        if status.is_server_error(status_code):
            logger.error('error', extra=log_kwargs)
        elif status.is_client_error(status_code):
            logger.warning('warning', extra=log_kwargs)
        else:
            logger.info('info', extra=log_kwargs)
        response['log'] = log_kwargs
        return response

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(LoggingMixin, cls).as_view(*args, **kwargs)
        view = decorator_from_middleware(RequestLogMiddleware)(view)
        return view
