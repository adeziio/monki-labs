import argparse

import json

import threading

import webbrowser

from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer
)

from pathlib import Path

from urllib.parse import (
    parse_qs,
    urlencode,
    urlparse
)

import requests


TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

DEFAULT_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

DEFAULT_PORT = 8080

WAIT_TIMEOUT_SECONDS = 240


class AuthRedirectHandler(
    BaseHTTPRequestHandler
):

    def do_GET(
        self
    ):

        parsed = urlparse(
            self.path
        )

        params = parse_qs(
            parsed.query
        )

        self.server.auth_code = (
            params.get(
                "code",
                [None]
            )[0]
        )

        self.server.auth_error = (
            params.get(
                "error",
                [None]
            )[0]
        )

        self.server.done.set()

        message = (
            "Authorization received. You can close this tab "
            "and return to the terminal."
        )

        body = (
            f"<html><body><h3>{message}</h3></body></html>"
        ).encode(
            "utf-8"
        )

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(
                len(body)
            )
        )

        self.end_headers()

        self.wfile.write(
            body
        )

    def log_message(
        self,
        format,
        *args
    ):

        return


def build_authorization_url(
    client_id,
    redirect_uri,
    scope
):

    return (
        AUTH_ENDPOINT
        +
        "?"
        +
        urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": scope,
                "access_type": "offline",
                "prompt": "consent"
            }
        )
    )


def run_authorization_flow(
    client_id,
    client_secret,
    port,
    scope
):

    redirect_uri = (
        f"http://localhost:{port}/"
    )

    auth_url = build_authorization_url(
        client_id,
        redirect_uri,
        scope
    )

    done = threading.Event()

    try:

        server = ThreadingHTTPServer(
            (
                "127.0.0.1",
                port
            ),
            AuthRedirectHandler
        )

    except OSError as error:

        raise SystemExit(
            f"[OAUTH] Could not bind port {port}: {error}"
        )

    server.auth_code = None

    server.auth_error = None

    server.done = done

    server_thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    server_thread.start()

    print(
        "[OAUTH] Opening the browser to authorize the channel..."
    )

    print(
        f"[OAUTH] {auth_url}"
    )

    webbrowser.open(
        auth_url
    )

    done.wait(
        timeout=WAIT_TIMEOUT_SECONDS
    )

    server.shutdown()

    server.server_close()

    server_thread.join(
        timeout=5
    )

    if server.auth_error:

        raise SystemExit(
            f"[OAUTH] Authorization failed: {server.auth_error}"
        )

    if not server.auth_code:

        raise SystemExit(
            "[OAUTH] No authorization code was received "
            "(timed out after "
            f"{WAIT_TIMEOUT_SECONDS} seconds?)."
        )

    return exchange_code(
        client_id,
        client_secret,
        redirect_uri,
        server.auth_code
    )


def exchange_code(
    client_id,
    client_secret,
    redirect_uri,
    code
):

    response = requests.post(
        TOKEN_ENDPOINT,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        },
        timeout=30
    )

    if response.status_code != 200:

        raise SystemExit(
            "[OAUTH] Token exchange failed: "
            f"HTTP {response.status_code} "
            f"{response.text[:300]}"
        )

    return response.json()


def save_account_to_config(
    client_id,
    client_secret,
    refresh_token
):

    config_path = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        /
        "config"
        /
        "youtube.json"
    )

    config = json.loads(
        config_path.read_text(
            encoding="utf-8"
        )
    )

    existing_account = config.get("account") or {}

    config["account"] = {
        "channel_name": str(
            existing_account.get("channel_name") or ""
        ).strip(),
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    text = json.dumps(
        config,
        indent=4,
        ensure_ascii=False
    )

    text = (
        text
        .replace(
            "\n",
            "\r\n"
        )
        +
        "\r\n"
    )

    config_path.write_text(
        text,
        encoding="utf-8",
        newline=""
    )

    print(
        "[OAUTH] Saved OAuth credentials "
        f"in {config_path}"
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Grab YouTube OAuth tokens (access + refresh) for the "
            "upload feature."
        )
    )

    parser.add_argument(
        "--client-id",
        default="",
        help="OAuth 2.0 client id (xxx.apps.googleusercontent.com)."
    )

    parser.add_argument(
        "--client-secret",
        default="",
        help="OAuth 2.0 client secret."
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=(
            "Local port the browser redirects to "
            f"(default {DEFAULT_PORT})."
        )
    )

    parser.add_argument(
        "--scope",
        default=DEFAULT_SCOPE,
        help="OAuth scope (default: youtube.upload)."
    )

    args = parser.parse_args()

    client_id = str(
        args.client_id
    ).strip()

    client_secret = str(
        args.client_secret
    ).strip()

    if not client_id:

        client_id = input(
            "OAuth Client ID: "
        ).strip()

    if not client_secret:

        client_secret = input(
            "OAuth Client Secret: "
        ).strip()

    if not client_id or not client_secret:

        raise SystemExit(
            "[OAUTH] Both Client ID and Client Secret are required."
        )

    tokens = run_authorization_flow(
        client_id,
        client_secret,
        args.port,
        args.scope
    )

    access_token = str(
        tokens.get(
            "access_token",
            ""
        )
    )

    refresh_token = str(
        tokens.get(
            "refresh_token",
            ""
        )
    )

    expires_in = tokens.get(
        "expires_in",
        "?"
    )

    print()

    print(
        "=============== ACCOUNT CREDENTIALS ==============="
    )

    print(
        f"Access Token (valid ~{expires_in} seconds):"
    )

    print(
        access_token
    )

    print(
        "Refresh Token:"
    )

    print(
        refresh_token
    )

    print(
        "==================================================="
    )

    if not refresh_token:

        print(
            "[OAUTH] No refresh token was returned. Make sure the "
            "OAuth client uses loopback (Desktop/Web with a "
            "localhost redirect) and consent was granted."
        )

    save_account_to_config(
            client_id,
            client_secret,
            refresh_token
    )


if __name__ == "__main__":

    main()
