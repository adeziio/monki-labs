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
            config,
            "PROMPT"
        )

        self.llm = OllamaProvider(
            config
        )

        content_config = (
            config["content"]
        )

        active_category = (
            content_config[
                "active_category"
            ]
        )

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

        self.generation_config = (
            self.category_config.get(
                "generation",
                {}
            )
        )

    def format_list(
        self,
        values,
        separator=", "
    ):

        if not isinstance(
            values,
            list
        ):

            return ""

        return separator.join(
            str(value).strip()
            for value in values
            if str(value).strip()
        )

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
            f"- {value}"
            for value in values
            if str(value).strip()
        )

    def build_prompt(
        self,
        count
    ):

        genre = (
            self.category_config.get(
                "genre",
                ""
            )
        )

        tone = (
            self.category_config.get(
                "tone",
                []
            )
        )

        world = (
            self.category_config.get(
                "world",
                []
            )
        )

        protagonists = (
            self.category_config.get(
                "protagonists",
                []
            )
        )

        comedy_types = (
            self.category_config.get(
                "comedy_types",
                []
            )
        )

        rules = (
            self.category_config.get(
                "rules",
                []
            )
        )

        creative_directions = (
            self.prompt_config.get(
                "creative_directions",
                []
            )
        )

        creative_priorities = (
            self.prompt_config.get(
                "creative_priorities",
                []
            )
        )

        viral_questions = (
            self.prompt_config.get(
                "viral_questions",
                []
            )
        )

        diversity_rules = (
            self.prompt_config.get(
                "diversity_rules",
                []
            )
        )

        prompt_format = (
            self.prompt_config.get(
                "prompt_format",
                {}
            )
        )

        visual_style = (
            self.generation_config.get(
                "visual_style",
                ""
            )
        )

        motion_style = (
            self.generation_config.get(
                "motion_style",
                ""
            )
        )

        camera_style = (
            self.generation_config.get(
                "camera_style",
                ""
            )
        )

        style_parts = [
            visual_style,
            motion_style,
            camera_style
        ]

        style_suffix = (
            self.format_list(
                style_parts
            )
        )

        include_text = (
            self.format_bullets(
                prompt_format.get(
                    "include",
                    []
                )
            )
        )

        exclude_text = (
            self.format_bullets(
                prompt_format.get(
                    "exclude",
                    []
                )
            )
        )

        paragraph_count = (
            prompt_format.get(
                "paragraphs",
                1
            )
        )

        minimum_words = (
            prompt_format.get(
                "minimum_words",
                25
            )
        )

        maximum_words = (
            prompt_format.get(
                "maximum_words",
                45
            )
        )

        return f"""
Generate exactly {count} original short-form video concepts.

The goal is to create visually strong ideas that make someone stop scrolling.

Think like a creative visual content creator, not a screenplay writer.

CORE CREATIVE PRINCIPLE

Design ONE strong visual premise.

The premise should be understandable almost immediately and become more interesting through one surprising visual development.

Do not write a miniature story.

Do not describe a chain of events just because the prompt needs to be longer.

A powerful visual contradiction, unusual situation, strange behavior, clever reveal, or unexpected outcome is better than several ordinary actions.

Prefer:

- one memorable visual premise
- one main character
- one recognizable environment
- one clear visual development
- one strong final image when appropriate

Avoid:

- long sequences of actions
- step-by-step storytelling
- multiple unrelated events
- generic slapstick
- random chaos
- arbitrary endings
- unnecessary movement

The viewer should be able to understand the basic joke or visual curiosity without dialogue, narration, or text.

CREATIVE DIRECTION

Start with the unusual visual idea rather than a normal setup.

Look for:

- visual contradictions
- unexpected scale
- strange behavior treated seriously
- familiar situations with one absurd twist
- impossible reflections or appearances
- unexpected character abilities
- characters misunderstanding what they see
- surprising visual consequences
- ironic visual outcomes
- unusual interactions between character and environment

The character should actively create or reveal the interesting situation.

Do not force a goal, obstacle, escalation, reaction, or traditional payoff.

If the strongest idea is simply a strange visual situation with one excellent reveal, use that.

CHARACTER

When a character is present:

- make the character visually distinctive
- give it readable body language
- make its behavior meaningful
- keep the character central to the visual idea

Do not make the character perform several minor actions.

Choose the fewest actions necessary to communicate the idea.

VARIETY

Every concept must explore different creative territory.

Vary:

- protagonist
- environment
- visual premise
- scale
- behavior
- comedic mechanism
- type of surprise
- ending

Do not simply change the animal while keeping the same joke.

Do not repeatedly use mirrors, vacuums, falling, chasing, panic, or similar mechanisms.

CATEGORY

GENRE:
{genre}

TONE:
{self.format_list(tone)}

WORLD:
{self.format_list(world)}

POSSIBLE PROTAGONISTS:
{self.format_list(protagonists)}

POSSIBLE CREATIVE DIRECTIONS:
{self.format_list(comedy_types)}

CATEGORY RULES:
{self.format_bullets(rules)}

CREATIVE DIRECTIONS:
{self.format_bullets(creative_directions)}

CREATIVE PRIORITIES:
{self.format_bullets(creative_priorities)}

VIRAL QUESTIONS:
{self.format_bullets(viral_questions)}

DIVERSITY:
{self.format_bullets(diversity_rules)}

PROMPT FORMAT

Write each prompt as exactly {paragraph_count} paragraph(s).

Write approximately {minimum_words}-{maximum_words} words.

Include:

{include_text}

Avoid:

{exclude_text}

The prompt should describe the visual premise naturally.

Do not pad the prompt with extra actions.

Do not include:

- dialogue
- narration
- text on screen
- timing or duration instructions
- previous or future clips
- continuity references
- abstract explanations
- instructions to the video model
- unnecessary choreography

STYLE

End each prompt with:

{style_suffix}

OUTPUT

Return exactly {count} concepts.

Use exactly this JSON structure:

[
    {{
        "title": "Short memorable title",
        "prompt": "Complete visual generation prompt"
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

                self.log(
                    "Skipping generated concept with no title."
                )

                continue

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

        if start == -1:

            return []

        depth = 0
        in_string = False
        escaped = False

        for index in range(
            start,
            len(response)
        ):

            character = (
                response[index]
            )

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

                    candidate = (
                        response[
                            start:index + 1
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