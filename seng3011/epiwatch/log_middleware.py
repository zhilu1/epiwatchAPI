from datetime import datetime, timezone


class RequestLogMiddleware(object):
    def process_request(self, request):
        utc_dt = datetime.now(timezone.utc)  # UTC time
        request.start_time = utc_dt
