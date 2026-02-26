"""Tests for Write.as publisher integration."""

from unittest.mock import MagicMock, patch

import pytest

from moka_news.writeas import WriteAsPublisher, WriteAsPublisherError


def _mock_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def test_writeas_publisher_is_configured_for_alias_pass():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "alice",
            "pass": "secret",
        }
    )

    assert publisher.is_configured() is True


def test_writeas_publisher_is_not_configured_without_alias_pass():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "",
            "pass": "",
        }
    )

    assert publisher.is_configured() is False


def test_publish_post_success_with_login_and_collection():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "alice",
            "pass": "secret",
            "collection_alias": "my-blog",
            "font": "serif",
            "lang": "it",
        }
    )

    login_response = {
        "code": 200,
        "data": {
            "access_token": "token-abc",
        },
    }
    create_response = {
        "code": 201,
        "data": {
            "id": "abc123",
            "slug": "morning-editorial",
            "title": "Morning Editorial",
            "body": "Editorial body",
        },
    }

    with patch(
        "moka_news.writeas.requests.post",
        side_effect=[
            _mock_response(login_response),
            _mock_response(create_response, status_code=201),
        ],
    ) as mock_post:
        result = publisher.publish_post(
            title="Morning Editorial",
            content="Editorial body",
        )

    assert result["id"] == "abc123"
    assert result["url"] == "https://write.as/my-blog/morning-editorial"
    assert mock_post.call_count == 2

    login_call = mock_post.call_args_list[0].kwargs
    create_call = mock_post.call_args_list[1].kwargs
    assert login_call["json"]["alias"] == "alice"
    assert login_call["json"]["pass"] == "secret"
    assert create_call["headers"]["Authorization"] == "Token token-abc"
    assert create_call["json"]["body"] == "Editorial body"
    assert create_call["json"]["font"] == "serif"
    assert create_call["json"]["lang"] == "it"


def test_publish_post_raises_when_disabled():
    publisher = WriteAsPublisher({"enabled": False})

    with pytest.raises(WriteAsPublisherError, match="disabled"):
        publisher.publish_post("Title", "Body")


def test_publish_post_raises_for_empty_content():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "alice",
            "pass": "secret",
        }
    )

    with pytest.raises(WriteAsPublisherError, match="cannot be empty"):
        publisher.publish_post("Title", "   ")


def test_publish_post_raises_for_api_error():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "alice",
            "pass": "secret",
        }
    )

    error_payload = {
        "code": 403,
        "error_msg": "forbidden",
    }

    with patch(
        "moka_news.writeas.requests.post",
        side_effect=[
            _mock_response({"code": 200, "data": {"access_token": "token-abc"}}),
            _mock_response(error_payload, status_code=403),
        ],
    ):
        with pytest.raises(WriteAsPublisherError, match="forbidden"):
            publisher.publish_post("Title", "Body")


def test_publish_post_raises_for_missing_alias_pass():
    publisher = WriteAsPublisher({"enabled": True, "alias": "", "pass": ""})

    with pytest.raises(WriteAsPublisherError, match="alias/pass"):
        publisher.publish_post("Title", "Body")


def test_publish_post_strips_leading_duplicate_markdown_title():
    publisher = WriteAsPublisher(
        {
            "enabled": True,
            "alias": "alice",
            "pass": "secret",
        }
    )

    login_response = {"code": 200, "data": {"access_token": "token-abc"}}
    create_response = {"code": 201, "data": {"id": "post-1", "slug": "post-1"}}

    content = """# Morning Editorial

*Thursday, February 26, 2026 at 08:00*

---

Main body paragraph.
"""

    with patch(
        "moka_news.writeas.requests.post",
        side_effect=[
            _mock_response(login_response),
            _mock_response(create_response, status_code=201),
        ],
    ) as mock_post:
        publisher.publish_post("Morning Editorial", content)

    create_call = mock_post.call_args_list[1].kwargs
    sent_body = create_call["json"]["body"]

    assert not sent_body.startswith("# Morning Editorial")
    assert "Main body paragraph." in sent_body
