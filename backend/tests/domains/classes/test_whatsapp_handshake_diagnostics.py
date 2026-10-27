"""Provider verification failures are diagnosable without putting credentials in host logs."""
import logging

import pytest
from marshmallow import ValidationError

from src.domains.classes.whatsapp.schemas.whatsapp_schemas import HandshakeSchema


@pytest.mark.parametrize("query, expected", [
    ({}, "present=[] alternate=[]"),
    ({"hub_mode": "subscribe", "hub_verify_token": "private-token", "hub_challenge": "123"},
     "alternate=['hub_mode', 'hub_verify_token', 'hub_challenge']"),
    ({"hub.mode": "subscribe", "hub.verify_token": "private-token", "hub.challenge": "<private-challenge>",
      "private-field-name": "private-field-value"}, "unknown_count=1"),
])
def test_rejected_handshakes_log_only_fixed_field_names_and_counts(caplog, query, expected):
    with caplog.at_level(logging.WARNING, logger="campus_chommie.whatsapp"):
        with pytest.raises(ValidationError):
            HandshakeSchema().load(query)
    assert expected in caplog.text
    assert "whatsapp_handshake_invalid" in caplog.text
    for private in ("private-token", "private-challenge", "private-field-name", "private-field-value"):
        assert private not in caplog.text


def test_valid_handshakes_keep_their_result_and_do_not_log(caplog):
    query = {"hub.mode": "subscribe", "hub.verify_token": "private-token", "hub.challenge": "123"}
    with caplog.at_level(logging.WARNING, logger="campus_chommie.whatsapp"):
        assert HandshakeSchema().load(query) == {
            "mode": "subscribe", "verify_token": "private-token", "challenge": "123",
        }
    assert "whatsapp_handshake_invalid" not in caplog.text
