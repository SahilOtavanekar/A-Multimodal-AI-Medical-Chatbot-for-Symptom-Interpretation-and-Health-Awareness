import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

logger = logging.getLogger("api_audit")

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            
            process_time = (time.time() - start_time) * 1000.0
            
            # Extract basic tracking info
            client_ip = request.client.host if request.client else "Unknown"
            status_code = response.status_code
            
            # Log the latency and status
            audit_message = f"Method: {request.method} Path: {request.url.path} Status: {status_code} Latency: {process_time:.2f}ms IP: {client_ip}"
            
            if status_code >= 500:
                logger.error(audit_message)
            elif status_code >= 400:
                logger.warning(audit_message)
            else:
                logger.info(audit_message)
                
            return response
            
        except Exception as e:
            # Handle unhandled errors that middleware catches
            process_time = (time.time() - start_time) * 1000.0
            client_ip = request.client.host if request.client else "Unknown"
            logger.critical(f"Method: {request.method} Path: {request.url.path} Status: 500 Latency: {process_time:.2f}ms IP: {client_ip} Exception: {str(e)}")
            raise e
