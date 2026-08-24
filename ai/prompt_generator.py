import json
import math
import random
import re
from pathlib import Path

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
            config,
            "PROMPT"
        )

        self.llm = OllamaProvider(
            config
        )

        content_config = config["content"]

        active_category = (
            content_config["active_category"]
        )

        self.category_name = active_category

        self.category_config = (
            content_config[
                "categories"
            ][
                active_category
            ]
        )

        self.prompt_config = (
            self.category_config.get(
                "prompt_generation",
                {}
            )
        )

        self.recent_concepts = []

    def pick_episode_setting(self):
        """
        Picks the next setting from the configured setting_rotation
        list in shuffled order - like a shuffled playlist. Every setting
        is used once per cycle before any repeats, the shuffle order is
        re-randomized at the start of each cycle, and the state is
        persisted per category because each episode job runs in a
        fresh process.
        """

        settings = [
            str(value).strip()
            for value in self.prompt_config.get(
                "setting_rotation",
                []
            )
            if str(value).strip()
        ]

        if not settings:

            return ""

        state_path = (
            Path("media")
            / "output"
            / ".prompt_state.json"
        )

        state = {}

        try:

            if state_path.exists():

                state = json.loads(
                    state_path.read_text(
                        encoding="utf-8"
                    )
                )

        except (
            json.JSONDecodeError,
            OSError
        ):

            state = {}

        order_key = (
            f"setting_order:{self.category_name}"
        )

        position_key = (
            f"setting_position:{self.category_name}"
        )

        last_key = (
            f"setting_last:{self.category_name}"
        )

        try:

            order = list(
                state.get(order_key, [])
            )

            position = int(
                state.get(position_key, 0)
            )

        except (
            TypeError,
            ValueError
        ):

            order = []

            position = 0

        # (Re)shuffle when there is no saved order yet or when the
        # configured settings list has changed since it was saved.

        if (
            not order
            or sorted(order) != list(range(len(settings)))
        ):

            order = list(range(len(settings)))

            random.shuffle(order)

            position = 0

        if position >= len(order):

            # Cycle complete: reshuffle for a fresh random order and
            # avoid repeating whatever played last.

            previous_last = state.get(last_key)

            order = list(range(len(settings)))

            random.shuffle(order)

            if (
                len(order) > 1
                and str(order[0]) == str(previous_last)
            ):
                order[0], order[-1] = (
                    order[-1],
                    order[0]
                )

            position = 0

        chosen_index = order[position]

        state[order_key] = order

        state[position_key] = position + 1

        state[last_key] = chosen_index

        try:

            state_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            state_path.write_text(
                json.dumps(
                    state,
                    indent=4
                ),
                encoding="utf-8"
            )

        except OSError:

            self.log(
                "Could not persist prompt "
                "setting rotation state."
            )

        setting = settings[chosen_index]

        self.log(
            f"Episode setting rotated to: {setting}"
        )

        return setting

    def format_bullets(
        self,
        values
    ):

        if not isinstance(
            values,
            list
        ):

            return ""

        return "\n".join(
            f"- {str(value).strip()}"
            for value in values
            if str(value).strip()
        )

    def build_shared_context_sections(self):

        genre = self.category_config.get(
            "genre",
            "short-form visual comedy"
        )

        tone = self.category_config.get(
            "tone",
            []
        )

        world = self.category_config.get(
            "world",
            []
        )

        protagonists = self.category_config.get(
            "protagonists",
            []
        )

        comedy_types = self.category_config.get(
            "comedy_types",
            []
        )

        absurdity_families = self.prompt_config.get(
            "absurdity_families",
            []
        )

        instructions = self.prompt_config.get(
            "instructions",
            []
        )

        creative_directions = self.prompt_config.get(
            "creative_directions",
            []
        )

        priorities = self.prompt_config.get(
            "creative_priorities",
            []
        )

        diversity = self.prompt_config.get(
            "diversity_guidance",
            []
        )

        return f"""GENRE
{genre}

TONE
{self.format_bullets(tone)}

POSSIBLE WORLDS
{self.format_bullets(world)}

POSSIBLE PROTAGONISTS
{self.format_bullets(protagonists)}

COMEDY ENGINES
{self.format_bullets(comedy_types)}

ABSURDITY FAMILIES
{self.format_bullets(absurdity_families)}

RECENT CONCEPTS TO AVOID REPEATING
{self.get_recent_concepts_text()}

RULES
{self.format_bullets(instructions)}

CREATIVE FREEDOM
{self.format_bullets(creative_directions)}

PRIORITIES
{self.format_bullets(priorities)}

VARIETY
{self.format_bullets(diversity)}

MAIN SUBJECT RULES
{self.format_bullets(self.prompt_config.get("living_subject_rules", []))}

WOW FACTOR
{self.format_bullets(self.prompt_config.get("wow_factor_guidance", []))}
"""

    def get_recent_concepts_text(self):

        recent_concepts = getattr(
            self,
            "recent_concepts",
            []
        )

        if not recent_concepts:

            return "- No previous concepts are available."

        return "\n".join(
            f"- {concept['title']}: {concept['prompt']}"
            for concept in recent_concepts[-8:]
        )

    def remember_concepts(self, concepts):

        self.recent_concepts.extend(
            concepts
        )

        self.recent_concepts = self.recent_concepts[
            -20:
        ]

    def get_prompt_word_range(self):

        video_config = (
            self.category_config.get(
                "video",
                {}
            )
        )

        prompt_format = (
            self.prompt_config.get(
                "prompt_format",
                {}
            )
        )

        try:

            duration_seconds = float(
                video_config.get(
                    "duration_seconds",
                    8
                )
            )

        except (
            TypeError,
            ValueError
        ):

            duration_seconds = 8.0

        if duration_seconds <= 0:

            duration_seconds = 8.0

        try:

            minimum_rate = float(
                prompt_format.get(
                    "minimum_words_per_second",
                    2.75
                )
            )

            maximum_rate = float(
                prompt_format.get(
                    "maximum_words_per_second",
                    4.75
                )
            )

            minimum_floor = int(
                prompt_format.get(
                    "minimum_words_floor",
                    12
                )
            )

            maximum_cap = int(
                prompt_format.get(
                    "maximum_words_cap",
                    80
                )
            )

        except (
            TypeError,
            ValueError
        ):

            minimum_rate = 2.75
            maximum_rate = 4.75
            minimum_floor = 12
            maximum_cap = 80

        minimum_words = max(
            minimum_floor,
            math.ceil(
                duration_seconds * minimum_rate
            )
        )

        maximum_words = min(
            maximum_cap,
            math.floor(
                duration_seconds * maximum_rate
            )
        )

        maximum_words = max(
            minimum_words,
            maximum_words
        )

        return {
            "duration_seconds": duration_seconds,
            "minimum_words": minimum_words,
            "maximum_words": maximum_words
        }

    def build_prompt(
        self,
        count
    ):

        word_range = self.get_prompt_word_range()

        duration_seconds = word_range[
            "duration_seconds"
        ]

        minimum_words = word_range[
            "minimum_words"
        ]

        maximum_words = word_range[
            "maximum_words"
        ]

        ltx2_rules = self.prompt_config.get(
            "ltx2_prompt_rules",
            []
        )

        audio_guidance = self.prompt_config.get(
            "audio_guidance",
            []
        )

        episode_setting = self.pick_episode_setting()

        setting_section = ""

        if episode_setting:

            setting_section = f"""
THIS EPISODE'S SETTING

Every concept in this batch must take place in: {episode_setting}.
State the setting explicitly inside the paragraph. Do not choose a
different location and do not default to an office, kitchen, or any
other familiar indoor space.
"""

        return f"""Generate exactly {count} original video concepts.

For each concept, write a single FULL generation prompt that is ready to be
fed directly into the video model. The full prompt must contain every visual
and every audio element in one continuous paragraph.

{self.build_shared_context_sections()}
{setting_section}
MUSIC AND SOUND FX (derive dynamically from the concept)
{self.format_bullets(audio_guidance)}

LTX2 PROMPT STRUCTURE (the "prompt" field, follow strictly)
{self.format_bullets(ltx2_rules)}

PROMPT LENGTH

Write the full "prompt" paragraph in approximately
{minimum_words}-{maximum_words} words. This range is derived from the
configured video duration of approximately
{duration_seconds:g} seconds. The paragraph must be long enough to cover the
style, the living subject, the impossible mutation, one escalation, and the
chronologically integrated music and sound effects - and short enough that a
single 8-second continuous shot can show all of it.

Use this exact narrative arc inside the full paragraph:
recognizable everyday setup -> one impossible physical mutation or behavior ->
one escalating action -> a concrete final image (with its final sound).

OUTPUT

Return exactly {count} concepts. Use exactly this JSON structure:

[
    {{
        "title": "Short memorable title",
        "prompt": "THE COMPLETE single-paragraph video+audio prompt"
    }}
]

Return ONLY the JSON array.
No markdown.
No code block.
No explanation.
No commentary.
"""

    def generate(
        self,
        count
    ):

        self.log(
            f"Generating {count} video prompts"
        )

        return self.generate_single_stage(
            count
        )

    def generate_single_stage(
        self,
        count
    ):

        prompt = self.build_prompt(
            count
        )

        response = self.llm.generate(
            prompt,
            response_format=self.get_response_schema()
        )

        prompts = self.parse_response(
            response,
            count
        )

        if not prompts:

            raise RuntimeError(
                "Prompt generator returned no usable prompts. "
                f"Raw response: {str(response)[:500]}"
            )

        return prompts

    def get_response_schema(self):

        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "prompt": {
                        "type": "string"
                    }
                },
                "required": [
                    "title",
                    "prompt"
                ],
                "additionalProperties": False
            }
        }

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

        data = None

        try:

            data = json.loads(
                response
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            self.log(
                "Prompt generator returned non-direct JSON. "
                "Attempting JSON array extraction."
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
                "Prompt generator did not return a JSON list."
            )

            return []

        requested_count = max(
            int(count),
            1
        )

        prompts = []

        for item in data:

            if not isinstance(
                item,
                dict
            ):

                continue

            title = str(
                item.get(
                    "title",
                    ""
                )
            ).strip()

            prompt = str(
                item.get(
                    "prompt",
                    ""
                )
            ).strip()

            if not title:

                title = " ".join(
                    prompt.split()[:6]
                ).strip(" ,.-") or "Untitled Concept"

                self.log(
                    "Concept had no title; "
                    "derived one from the prompt."
                )

            if not prompt:

                self.log(
                    f"Skipping '{title}' because "
                    "the prompt is empty."
                )

                continue

            prompts.append(
                {
                    "title": title,
                    "prompt": prompt
                }
            )

        if not prompts:

            self.log(
                "Prompt generator parsed zero usable prompts."
            )

            return []

        if len(prompts) < requested_count:

            self.log(
                f"Model returned {len(prompts)} usable prompts "
                f"out of {requested_count} requested."
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

        self.remember_concepts(
            prompts
        )

        return prompts

    def validate_prompt(
        self,
        prompt
    ):

        if not isinstance(
            prompt,
            str
        ):

            return False

        return bool(
            prompt.strip()
        )

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

        if start == -1:

            return []

        depth = 0
        in_string = False
        escaped = False

        for index in range(
            start,
            len(response)
        ):

            character = response[index]

            if escaped:

                escaped = False
                continue

            if character == "\\" and in_string:

                escaped = True
                continue

            if character == '"':

                in_string = not in_string
                continue

            if in_string:

                continue

            if character == "[":

                depth += 1

            elif character == "]":

                depth -= 1

                if depth == 0:

                    candidate = response[
                        start:index + 1
                    ]

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

        return []

    def repair_json_array(
        self,
        value
    ):

        if not value:

            return value

        repaired = value.strip()

        repaired = repaired.replace(
            "\\,",
            ","
        )

        repaired = repaired.replace(
            "\\/",
            "/"
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
