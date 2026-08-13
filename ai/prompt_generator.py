import json
import re

from ai.base_ai_service import BaseAIService
from ai.providers.ollama_provider import OllamaProvider


class PromptGenerator(
    BaseAIService
):

    def __init__(
        self,
        config
    ):

        super().__init__(
            config
        )

        self.config = config

        self.llm = OllamaProvider(
            config
        )

        content_config = (
            config["content"]
        )

        self.active_category = (
            content_config[
                "active_category"
            ]
        )

        self.category_config = (
            content_config[
                "categories"
            ][
                self.active_category
            ]
        )

        self.prompt_config = (
            self.category_config
            .get(
                "prompt_generation",
                {}
            )
        )

    def build_prompt(
        self,
        count
    ):

        genre = (
            self.category_config
            .get(
                "genre",
                ""
            )
        )

        tone = (
            self.category_config
            .get(
                "tone",
                []
            )
        )

        world = (
            self.category_config
            .get(
                "world",
                []
            )
        )

        categories = (
            self.prompt_config
            .get(
                "categories",
                []
            )
        )

        requirements = (
            self.prompt_config
            .get(
                "requirements",
                []
            )
        )

        tone_text = ", ".join(
            str(item)
            for item in tone
        )

        world_text = ", ".join(
            str(item)
            for item in world
        )

        category_text = ", ".join(
            str(item)
            for item in categories
        )

        requirement_text = "\n".join(
            f"- {item}"
            for item in requirements
        )

        return f"""
Generate exactly {count} independent short-form AI video concepts.

These concepts will be converted directly from text into short AI video
clips.

There is NO story continuity.

Each concept must work completely independently.

GENRE:
{genre}

TONE:
{tone_text}

WORLD:
{world_text}

POSSIBLE CONCEPT CATEGORIES:
{category_text}

REQUIREMENTS:
{requirement_text}

IMPORTANT:

Return exactly {count} concepts.

Each concept should describe one visually interesting situation.

The viewer should understand the basic visual idea immediately.

Prioritize:

- visual curiosity
- absurdity
- unexpected physical behavior
- unusual scale
- surprising movement
- visual comedy
- strange objects
- impossible situations
- quick escalation
- strong visual payoff

Do not create traditional stories.

Do not create multi-scene narratives.

Do not reference previous or future clips.

Do not use recurring characters.

Do not use character names.

Do not require dialogue.

Do not require narration.

Do not explain why something is funny.

Simply describe what should visibly happen.

Keep each prompt concise enough for a text-to-video model.

Return ONLY the JSON array.

Do not include markdown.

Do not include a code block.

Do not include an explanation.

Example:

[
    "A tiny elephant struggles to push an enormous beach ball across a crowded beach before the ball suddenly rolls downhill.",
    "A vending machine starts shaking violently before launching colorful drinks into the air.",
    "A giant rubber duck bounces through a miniature city and accidentally knocks over a skyscraper."
]
"""

    def generate(
        self,
        count
    ):

        self.log(
            f"Generating {count} video prompts"
        )

        prompt = (
            self.build_prompt(
                count
            )
        )

        response = (
            self.llm.generate(
                prompt
            )
        )

        return self.parse_response(
            response,
            count
        )

    def parse_response(
        self,
        response,
        count
    ):

        if not response:

            self.log(
                "Prompt generator returned an empty response."
            )

            return []

        response = (
            self.clean_response(
                response
            )
        )

        if not response:

            self.log(
                "Prompt generator returned no usable content."
            )

            return []

        try:

            data = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            self.log(
                "Prompt generator returned invalid JSON."
            )

            data = (
                self.extract_json_array(
                    response
                )
            )

        if not isinstance(
            data,
            list
        ):

            self.log(
                "Prompt generator did not return a list."
            )

            return []

        prompts = []

        for item in data:

            if not isinstance(
                item,
                str
            ):

                continue

            item = item.strip()

            if not item:

                continue

            prompts.append(
                item
            )

        if not prompts:

            self.log(
                "Prompt generator returned no valid prompts."
            )

            return []

        requested_count = max(
            int(count),
            1
        )

        if len(prompts) > requested_count:

            self.log(
                f"Model returned {len(prompts)} prompts. "
                f"Using the requested {requested_count}."
            )

            prompts = prompts[
                :requested_count
            ]

        self.log(
            f"Generated {len(prompts)} usable video prompts"
        )

        return prompts

    def clean_response(
        self,
        response
    ):

        if not isinstance(
            response,
            str
        ):

            return ""

        cleaned = response.strip()

        if not cleaned:

            return ""

        if "```" in cleaned:

            cleaned = re.sub(
                r"```(?:json)?",
                "",
                cleaned,
                flags=re.IGNORECASE
            )

            cleaned = cleaned.replace(
                "```",
                ""
            )

            cleaned = cleaned.strip()

        return cleaned

    def extract_json_array(
        self,
        response
    ):

        if not response:

            return []

        start = response.find(
            "["
        )

        end = response.rfind(
            "]"
        )

        if (
            start == -1
            or
            end == -1
            or
            end <= start
        ):

            return []

        candidate = (
            response[
                start:end + 1
            ]
        )

        try:

            return json.loads(
                candidate
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            repaired = (
                self.repair_json_array(
                    candidate
                )
            )

            try:

                return json.loads(
                    repaired
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                return []

    def repair_json_array(
        self,
        value
    ):

        if not value:

            return value

        repaired = value.strip()

        repaired = (
            repaired.replace(
                "\\,",
                ","
            )
        )

        repaired = (
            repaired.replace(
                "\\/",
                "/"
            )
        )

        repaired = re.sub(
            r'"\s*,\s*\\\s*,',
            '",',
            repaired
        )

        repaired = re.sub(
            r'"\s*,\s*\\\s*"',
            '", "',
            repaired
        )

        repaired = re.sub(
            r'\\\s*,\s*\\',
            ',',
            repaired
        )

        repaired = re.sub(
            r'\\\s*$',
            '',
            repaired
        )

        return repaired