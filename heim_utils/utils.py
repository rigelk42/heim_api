from datetime import datetime


def generate_customer_id():
    """
    Generate a timestamp-based ID string.

    Format: CHHMMSSS-YYDDD where:
    - The letter "C"
    - HH: Two digits for hour (00-23)
    - MM: Two digits for minute (00-59)
    - SSS: Three digits for seconds (000-059)
    - YY: Last two digits of the year
    - DDD: Three digits for day of year (001-366)

    Returns:
        str: A timestamp-based ID string (e.g., "C1205330-25001")
    """
    now = datetime.now()

    # Last two digits of year
    year = now.strftime("%y")

    # Day of year (001-366)
    day_of_year = now.strftime("%j")

    # Hour (00-23)
    hour = now.strftime("%H")

    # Minute (00-59)
    minute = now.strftime("%M")

    # Seconds with three digits (000-059)
    seconds = now.strftime("%S").zfill(3)

    return f"C{hour}{minute}{seconds}-{year}{day_of_year}"


from rest_framework.response import Response


def generic_api_response(status, data=None, error=None):
    """
    Generate a standardized API response.
    """
    return Response(
        {
            "status": status,
            "error": error,
            "data": data,
        }
    )
