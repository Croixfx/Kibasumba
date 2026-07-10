import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_to_e164(phone_number):
    """
    Twilio only accepts international E.164 numbers, so convert the local
    Rwandan format 07XXXXXXXX to +2507XXXXXXXX. Numbers already starting
    with + are passed through unchanged.
    """
    if phone_number.startswith("0"):
        return "+250" + phone_number[1:]
    return phone_number


def send_sms(phone_number, message):
    """
    Send an SMS to phone_number.

    With SMS_BACKEND='twilio' (set in backend/.env) this sends a real SMS;
    otherwise it just logs/prints the message for local development.
    """
    if settings.SMS_BACKEND == "twilio":
        _send_via_twilio(normalize_to_e164(phone_number), message)
    else:
        logger.info("SMS to %s: %s", phone_number, message)
        print(f"[SMS to {phone_number}] {message}")


def _send_via_twilio(phone_number, message):
    if not (
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_FROM_NUMBER
    ):
        raise RuntimeError(
            "SMS_BACKEND is 'twilio' but TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN "
            "or TWILIO_FROM_NUMBER is missing. Fill them in backend/.env."
        )

    # Imported lazily so the console backend works even without the twilio
    # package installed.
    from twilio.base.exceptions import TwilioException
    from twilio.rest import Client

    # Delivery failures (e.g. unverified recipient on a trial account) must
    # not break the API call that triggered the SMS — the account/OTP is
    # still created; the failure is logged for the developer.
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        result = client.messages.create(
            to=phone_number,
            from_=settings.TWILIO_FROM_NUMBER,
            body=message,
        )
    except TwilioException as e:
        logger.error("Twilio SMS to %s FAILED: %s", phone_number, e)
        print(f"[SMS FAILED to {phone_number}] {e}")
        print(f"[SMS body was] {message}")
        return
    logger.info("Twilio SMS sent to %s (sid=%s)", phone_number, result.sid)
