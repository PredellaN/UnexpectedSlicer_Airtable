from typing import Any
import requests, functools

def measure_performance(func): #type: ignore
    @functools.wraps(func)
    def wrapper(*args, **kwargs): #type: ignore
        # Keep a reference to the original requests.get
        original_get = requests.get

        def monitored_get(url: str, headers: dict[str, str] = {}, **get_kwargs): #type: ignore
            response = original_get(url, headers=headers, **get_kwargs)
            # Use response.elapsed for latency (in ms)
            latency = response.elapsed.total_seconds() * 1000
            # Calculate sizes:
            response_size = len(response.content)
            # Compute request size as the sum of header value lengths and the URL length.
            req_size = (sum(len(str(v)) for v in headers.values()) if headers else 0) + len(url)
            print(f"Latency: {latency:.2f} ms")
            print(f"Request size: {req_size} bytes, Response size: {response_size} bytes")
            return response

        # Monkey-patch requests.get inside the decorated function.
        requests.get = monitored_get
        try:
            result = func(*args, **kwargs)
        finally:
            # Restore the original requests.get, even if an exception occurs.
            requests.get = original_get
        return result

    return wrapper