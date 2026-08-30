import json
import logging


SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "nin",
    "bvn",
    "card_number",
}


def mask_sensitive_data(data: dict) -> dict:
    masked_data = {}

    for key, value in data.items():
        if key.lower() in SENSITIVE_FIELDS:
            masked_data[key] = "***"
        else:
            masked_data[key] = value

    return masked_data


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "path"):
            log_data["path"] = record.path

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms

        return json.dumps(mask_sensitive_data(log_data))


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

if not logger.handlers:
    logger.addHandler(handler)