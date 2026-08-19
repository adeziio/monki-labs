from pathlib import Path
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer
)
from urllib.parse import (
    urlparse,
    unquote
)
import json
import threading
import traceback

from core.pipeline import MonkiPipeline


HOST = "0.0.0.0"
PORT = 8000

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

MEDIA_ROOT = (
    PROJECT_ROOT
    /
    "media"
    /
    "output"
)

INDEX_FILE = (
    Path(__file__).resolve().parent
    /
    "index.html"
)


pipeline = MonkiPipeline()

job_lock = threading.Lock()

job_state = {
    "running": False,
    "type": None,
    "progress": 0,
    "message": "Ready.",
    "error": None,
    "result": None
}


def set_progress(
    percent,
    message
):

    job_state[
        "progress"
    ] = int(
        max(
            0,
            min(
                100,
                percent
            )
        )
    )

    job_state[
        "message"
    ] = str(
        message
    )


pipeline.set_progress_callback(
    set_progress
)


def parse_prompt_file(
    path
):

    text = path.read_text(
        encoding="utf-8"
    )

    parts = text.split(
        "=" * 72
    )

    prompts = []

    for part in parts:

        title_marker = "TITLE:"
        prompt_marker = "PROMPT:"

        title_index = part.find(
            title_marker
        )

        prompt_index = part.find(
            prompt_marker
        )

        if (
            title_index == -1
            or
            prompt_index == -1
        ):

            continue

        title = (
            part[
                title_index
                +
                len(title_marker):
                prompt_index
            ]
            .strip()
        )

        prompt = (
            part[
                prompt_index
                +
                len(prompt_marker):
            ]
            .strip()
        )

        if not title or not prompt:

            continue

        prompts.append(
            {
                "title": title,
                "prompt": prompt
            }
        )

    return prompts


def discover_episodes():

    results = []

    if not MEDIA_ROOT.exists():

        return results

    for category_directory in sorted(
        MEDIA_ROOT.iterdir()
    ):

        if not category_directory.is_dir():

            continue

        for episode_directory in sorted(
            category_directory.iterdir(),
            reverse=True
        ):

            if not episode_directory.is_dir():

                continue

            if not episode_directory.name.isdigit():

                continue

            prompt_path = (
                episode_directory
                /
                "prompt.txt"
            )

            video_path = (
                episode_directory
                /
                "episode.mp4"
            )

            prompts = []

            if prompt_path.is_file():

                try:

                    prompts = parse_prompt_file(
                        prompt_path
                    )

                except Exception:

                    prompts = []

            prompt_item = (
                prompts[0]
                if prompts
                else None
            )

            try:

                relative_directory = (
                    episode_directory
                    .relative_to(
                        PROJECT_ROOT
                    )
                )

            except ValueError:

                continue

            episode_id = str(
                relative_directory
            ).replace(
                "\\",
                "/"
            )

            video_exists = (
                video_path.is_file()
            )

            video_relative_path = None

            if video_exists:

                try:

                    video_relative_path = str(
                        video_path
                        .relative_to(
                            MEDIA_ROOT
                        )
                    ).replace(
                        "\\",
                        "/"
                    )

                except ValueError:

                    video_relative_path = None

            results.append(
                {
                    "id": episode_id,
                    "number": episode_directory.name,
                    "category": category_directory.name,
                    "path": episode_id,
                    "prompt_exists": bool(
                        prompt_item
                    ),
                    "title": (
                        prompt_item["title"]
                        if prompt_item
                        else ""
                    ),
                    "prompt": (
                        prompt_item["prompt"]
                        if prompt_item
                        else ""
                    ),
                    "video_exists": video_exists,
                    "video_path": video_relative_path
                }
            )

    results.sort(
        key=lambda item: (
            item["category"],
            int(item["number"])
        ),
        reverse=True
    )

    return results


def get_prompt_by_id(
    prompt_id
):

    separator = "::"

    if separator not in prompt_id:

        raise ValueError(
            "Invalid prompt ID."
        )

    relative_path, index_text = (
        prompt_id.rsplit(
            separator,
            1
        )
    )

    index = int(
        index_text
    )

    prompt_path = (
        PROJECT_ROOT
        /
        Path(
            relative_path
        )
    ).resolve()

    allowed_root = (
        MEDIA_ROOT.resolve()
    )

    if (
        allowed_root
        not in prompt_path.parents
    ):

        raise ValueError(
            "Invalid prompt path."
        )

    if prompt_path.name != "prompt.txt":

        raise ValueError(
            "Invalid prompt file."
        )

    prompts = parse_prompt_file(
        prompt_path
    )

    if (
        index < 0
        or
        index >= len(prompts)
    ):

        raise ValueError(
            "Prompt no longer exists."
        )

    return prompts[index]


def get_episode_prompt(
    episode_id
):

    episode_path = (
        PROJECT_ROOT
        /
        Path(episode_id)
    ).resolve()

    allowed_root = (
        MEDIA_ROOT.resolve()
    )

    if (
        allowed_root
        not in episode_path.parents
    ):

        raise ValueError(
            "Invalid episode path."
        )

    if not episode_path.is_dir():

        raise ValueError(
            "Episode does not exist."
        )

    prompt_path = (
        episode_path
        /
        "prompt.txt"
    )

    if not prompt_path.is_file():

        raise ValueError(
            "Episode does not contain a prompt."
        )

    prompts = parse_prompt_file(
        prompt_path
    )

    if not prompts:

        raise ValueError(
            "Episode prompt is empty."
        )

    return prompts[0]


def run_job(
    job_type,
    function
):

    if not job_lock.acquire(
        blocking=False
    ):

        return False

    job_state[
        "running"
    ] = True

    job_state[
        "type"
    ] = job_type

    job_state[
        "progress"
    ] = 0

    job_state[
        "message"
    ] = "Starting..."

    job_state[
        "error"
    ] = None

    job_state[
        "result"
    ] = None

    def worker():

        try:

            result = function()

            job_state[
                "result"
            ] = result

            job_state[
                "progress"
            ] = 100

            job_state[
                "message"
            ] = "Complete."

        except Exception as error:

            traceback.print_exc()

            job_state[
                "error"
            ] = str(
                error
            )

            job_state[
                "message"
            ] = "Failed."

        finally:

            job_state[
                "running"
            ] = False

            job_state[
                "type"
            ] = None

            job_lock.release()

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()

    return True


class RequestHandler(
    BaseHTTPRequestHandler
):

    def log_message(
        self,
        format,
        *args
    ):

        return

    def send_json(
        self,
        data,
        status=200
    ):

        body = json.dumps(
            data
        ).encode(
            "utf-8"
        )

        self.send_response(
            status
        )

        self.send_header(
            "Content-Type",
            "application/json"
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

    def read_json(
        self
    ):

        length = int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        if length <= 0:

            return {}

        body = self.rfile.read(
            length
        )

        return json.loads(
            body.decode(
                "utf-8"
            )
        )

    def do_GET(
        self
    ):

        parsed = urlparse(
            self.path
        )

        path = parsed.path

        if path == "/":

            self.serve_index()

            return

        if path == "/api/status":

            self.send_json(
                job_state
            )

            return

        if path == "/api/episodes":

            self.send_json(
                discover_episodes()
            )

            return

        if path == "/api/prompts":

            episodes = discover_episodes()

            prompts = []

            for episode in episodes:

                if not episode[
                    "prompt_exists"
                ]:

                    continue

                prompts.append(
                    {
                        "id": (
                            f"{episode['path']}"
                            "::0"
                        ),
                        "path": (
                            f"{episode['path']}"
                            "/prompt.txt"
                        ),
                        "index": 0,
                        "title": episode[
                            "title"
                        ],
                        "prompt": episode[
                            "prompt"
                        ]
                    }
                )

            self.send_json(
                prompts
            )

            return

        if path.startswith(
            "/media/"
        ):

            self.serve_media(
                path[
                    len("/media/"):
                ]
            )

            return

        self.send_json(
            {
                "error": "Not found."
            },
            404
        )

    def do_POST(
        self
    ):

        parsed = urlparse(
            self.path
        )

        if parsed.path == "/api/episode":

            started = run_job(
                "episode",
                lambda:
                    pipeline.create_episode()
            )

            if not started:

                self.send_json(
                    {
                        "error":
                        "Another job is already running."
                    },
                    409
                )

                return

            self.send_json(
                {
                    "started": True
                }
            )

            return

        if parsed.path == "/api/video":

            try:

                data = self.read_json()

                episode_id = str(
                    data.get(
                        "episode_id",
                        ""
                    )
                ).strip()

                if not episode_id:

                    raise ValueError(
                        "Missing episode ID."
                    )

                prompt_item = (
                    get_episode_prompt(
                        episode_id
                    )
                )

            except Exception as error:

                self.send_json(
                    {
                        "error": str(
                            error
                        )
                    },
                    400
                )

                return

            started = run_job(
                "video",
                lambda:
                    pipeline.generate_video_from_prompt(
                        prompt_item,
                        episode_id
                    )
            )

            if not started:

                self.send_json(
                    {
                        "error":
                        "Another job is already running."
                    },
                    409
                )

                return

            self.send_json(
                {
                    "started": True
                }
            )

            return

        self.send_json(
            {
                "error": "Not found."
            },
            404
        )

    def serve_index(
        self
    ):

        try:

            body = INDEX_FILE.read_bytes()

        except OSError:

            self.send_json(
                {
                    "error":
                    "UI file not found."
                },
                500
            )

            return

        self.send_response(
            200
        )

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

    def serve_media(
        self,
        relative_path
    ):

        relative_path = unquote(
            relative_path
        )

        file_path = (
            MEDIA_ROOT
            /
            relative_path
        ).resolve()

        media_root = (
            MEDIA_ROOT.resolve()
        )

        if (
            media_root
            not in file_path.parents
        ):

            self.send_json(
                {
                    "error": "Invalid path."
                },
                403
            )

            return

        if not file_path.is_file():

            self.send_json(
                {
                    "error": "File not found."
                },
                404
            )

            return

        if file_path.suffix.lower() == ".mp4":

            content_type = "video/mp4"

        else:

            content_type = (
                "application/octet-stream"
            )

        try:

            file_size = file_path.stat().st_size

        except OSError:

            self.send_json(
                {
                    "error": "Could not read file."
                },
                500
            )

            return

        range_header = self.headers.get(
            "Range"
        )

        start = 0
        end = file_size - 1

        if range_header:

            try:

                if not range_header.startswith(
                    "bytes="
                ):

                    raise ValueError(
                        "Invalid range."
                    )

                range_value = (
                    range_header[
                        len("bytes="):
                    ]
                    .split(
                        ",",
                        1
                    )[0]
                    .strip()
                )

                if "-" not in range_value:

                    raise ValueError(
                        "Invalid range."
                    )

                start_text, end_text = (
                    range_value.split(
                        "-",
                        1
                    )
                )

                if start_text:

                    start = int(
                        start_text
                    )

                    if end_text:

                        end = int(
                            end_text
                        )

                    else:

                        end = (
                            file_size - 1
                        )

                else:

                    suffix_length = int(
                        end_text
                    )

                    if suffix_length <= 0:

                        raise ValueError(
                            "Invalid range."
                        )

                    start = max(
                        0,
                        file_size
                        -
                        suffix_length
                    )

                    end = (
                        file_size - 1
                    )

                if (
                    start < 0
                    or
                    start >= file_size
                    or
                    end < start
                ):

                    raise ValueError(
                        "Invalid range."
                    )

                end = min(
                    end,
                    file_size - 1
                )

            except (
                ValueError,
                TypeError
            ):

                self.send_response(
                    416
                )

                self.send_header(
                    "Content-Range",
                    f"bytes */{file_size}"
                )

                self.end_headers()

                return

            content_length = (
                end
                -
                start
                +
                1
            )

            self.send_response(
                206
            )

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(
                    content_length
                )
            )

            self.send_header(
                "Content-Range",
                f"bytes {start}-{end}/{file_size}"
            )

            self.send_header(
                "Accept-Ranges",
                "bytes"
            )

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.end_headers()

            try:

                with file_path.open(
                    "rb"
                ) as file:

                    file.seek(
                        start
                    )

                    remaining = (
                        content_length
                    )

                    while remaining > 0:

                        chunk_size = min(
                            1024 * 1024,
                            remaining
                        )

                        chunk = file.read(
                            chunk_size
                        )

                        if not chunk:

                            break

                        self.wfile.write(
                            chunk
                        )

                        remaining -= len(
                            chunk
                        )

            except (
                BrokenPipeError,
                ConnectionResetError
            ):

                return

            return

        self.send_response(
            200
        )

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(
                file_size
            )
        )

        self.send_header(
            "Accept-Ranges",
            "bytes"
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.end_headers()

        try:

            with file_path.open(
                "rb"
            ) as file:

                while True:

                    chunk = file.read(
                        1024 * 1024
                    )

                    if not chunk:

                        break

                    self.wfile.write(
                        chunk
                    )

        except (
            BrokenPipeError,
            ConnectionResetError
        ):

            return


def main():

    server = ThreadingHTTPServer(
        (
            HOST,
            PORT
        ),
        RequestHandler
    )

    print()
    print(
        "======================================"
    )
    print(
        "        MONKI LABS WEB UI"
    )
    print(
        "======================================"
    )
    print(
        f"Running on http://{HOST}:{PORT}"
    )
    print(
        "Open http://localhost:8000"
    )
    print(
        "======================================"
    )
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\n[SYSTEM] Shutting down."
        )

    finally:

        server.server_close()


if __name__ == "__main__":

    main()