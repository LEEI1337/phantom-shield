"""Tests for HMAC signing and verification."""

import time

from nss.gateway.hmac_signing import generate_nonce, sign_request, verify_request


def test_sign_and_verify() -> None:
    payload = '{"message": "hello"}'
    secret = "test-secret"
    timestamp = str(int(time.time()))
    nonce = generate_nonce()

    signature = sign_request(payload, secret, timestamp, nonce)
    assert verify_request(payload, signature, secret, timestamp, nonce)


def test_invalid_signature() -> None:
    payload = '{"message": "hello"}'
    secret = "test-secret"
    timestamp = str(int(time.time()))
    nonce = generate_nonce()

    assert not verify_request(payload, "invalid-sig", secret, timestamp, nonce)


def test_expired_timestamp() -> None:
    payload = '{"message": "hello"}'
    secret = "test-secret"
    old_timestamp = str(int(time.time()) - 600)
    nonce = generate_nonce()

    signature = sign_request(payload, secret, old_timestamp, nonce)
    assert not verify_request(payload, signature, secret, old_timestamp, nonce, max_age=300)


def test_different_payloads() -> None:
    secret = "test-secret"
    timestamp = str(int(time.time()))
    nonce = generate_nonce()

    sig1 = sign_request("payload1", secret, timestamp, nonce)
    sig2 = sign_request("payload2", secret, timestamp, nonce)
    assert sig1 != sig2
