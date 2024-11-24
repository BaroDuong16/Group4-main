import requests
import dns.resolver
from django.conf import settings
import re
import logging
from typing import Optional, Union
import inspect


def __check_ip_or_dns(input_string):
    local_service_pattern = re.compile(r'^[a-zA-Z0-9-_]+$')
                         
    ip_pattern = re.compile(
        r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    domain_pattern = re.compile(
        r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z]{2,})+$"
    )

    if ip_pattern.match(input_string):
        return "IP"
    elif domain_pattern.match(input_string):
        return "DNS"
    elif local_service_pattern.match(input_string):
        return "Local"
    else:
        return None


def __dns_to_ip(domain: str) -> str:
    answers = dns.resolver.resolve(domain, "A")
    return next(iter(answers)).address


def _request(
    api_name: str,
    json: dict,
    host: Optional[str] = None,
    port: Optional[str] = None,
    protocol: str = "http",
    verbose: bool = True,
):
    if host is None:
        host = settings.AI_API_SERVER["HOST"]
        port = settings.AI_API_SERVER["PORT"]

    base_url = "{}://{}:{}/{}"

    caller_frame = inspect.stack()[1]
    logger = logging.getLogger(f"{caller_frame.filename} => {caller_frame.function}()")

    try:
        checked_host = __check_ip_or_dns(host)

        if checked_host == "DNS":
            host = __dns_to_ip(host)

        protocol = protocol.lower()
        url = base_url.format(protocol, host, port, api_name)

        assert checked_host is not None, "Invalid Domain or IP!"

        if verbose:
            logger.info(f"Sending request to: '{url}'!")

        response = requests.post(url, json=json, timeout=5)
        # response.raise_for_status()

        message = response.json()["message"]
        is_error = False

    except AssertionError as e:
        message = e
        is_error = True
    except requests.exceptions.Timeout:
        message = "Request Timeout!"
        is_error = True
    except requests.exceptions.ConnectionError:
        message = "Connection error!"
        is_error = True
    except requests.exceptions.HTTPError as err:
        message = f"HTTP error occurred: {err}!"
        is_error = True
    except requests.exceptions.RequestException as err:
        message = f"An error occurred: {err}!"
        is_error = True
    except:
        message = f"Undetected error!"
        is_error = True
    finally:
        if is_error:
            if verbose:
                logger.error(message)
            return {"message": message}
        else:
            return response.json()


if __name__ == "__main__":
    valid_ip = "192.168.1.1"
    valid_dns = "truong51972.ddns.net"
    invalid = None

    api_name = "haah"
    data = {"test": "haha"}

    _request(api_name, data, invalid, "8000", verbose=True)
