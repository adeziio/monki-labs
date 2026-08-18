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

        category_guidance = (
            self.category_config.get(
                "prompt_guidance",
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

        visual_requirements = (
            self.prompt_config.get(
                "visual_requirements",
                []
            )
        )

        diversity_guidance = (
            self.prompt_config.get(
                "diversity_guidance",
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
            motion_style
        ]

        style_suffix = (
            self.format_list(
                style_parts
            )
        )

        format_include = (
            self.format_bullets(
                prompt_format.get(
                    "include",
                    []
                )
            )
        )

        format_exclude = (
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
                30
            )
        )

        maximum_words = (
            prompt_format.get(
                "maximum_words",
                55
            )
        )

        camera_instruction = ""

        if camera_style:

            camera_instruction = f"""
CAMERA

Use this configured camera style only when it helps communicate the action:

{camera_style}

Do not describe camera movement unless it improves clarity.
"""

        return f"""
Generate exactly {count} original short-form vertical video concepts.

CREATIVE GOAL

Create visually strong ideas that make someone want to keep watching.

Think like a creative short-form video creator.

The concept should be:

- immediately interesting
- visually clear
- memorable
- simple enough to generate reliably
- surprising, funny, strange, satisfying, emotional, or otherwise compelling
- understandable without dialogue or narration

Do not write a screenplay.

Do not force a traditional story structure.

Do not add actions simply to make the prompt longer.

One excellent visual idea is better than a complicated sequence.

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

CATEGORY GUIDANCE:
{self.format_bullets(category_guidance)}

CREATIVE DIRECTIONS:
{self.format_bullets(creative_directions)}

CREATIVE PRIORITIES:
{self.format_bullets(creative_priorities)}

VISUAL REQUIREMENTS

{self.format_bullets(visual_requirements)}

VISUAL CLARITY

Describe what the viewer should actually see.

When a character is important:

- make its appearance visually clear
- give it a visible face and readable eyes when appropriate
- make important body language obvious
- make the character actively cause the important events

When spatial relationships matter, describe them explicitly.

For example, prefer:

- facing the mirror
- looking directly at the object
- standing beside the door
- holding the object in both hands
- sitting inside the bathtub

instead of vague descriptions such as:

- near the mirror
- around the object
- in front of the door

Make important relationships visually unambiguous.

Use color when appropriate. Do not default to black-and-white or monochrome unless the concept specifically requires it.

Do not explain the joke.

Show the visual situation that creates the joke.

Keep the number of important actions low enough that the video model can represent them clearly.

VARIETY

Make every concept substantially different.

Vary:

- protagonist
- environment
- visual premise
- behavior
- scale
- situation
- emotional tone
- comedic mechanism
- outcome

Do not simply replace one character with another while keeping the same idea.

Do not repeatedly use the same locations, props, actions, or joke structures.

PROMPT FORMAT

Write each prompt as exactly {paragraph_count} paragraph(s).

Aim for approximately {minimum_words}-{maximum_words} words.

Include useful visual information such as:

{format_include}

Avoid:

{format_exclude}

Do not mention:

- seconds
- frames
- duration
- clip length
- timing instructions
- previous clips
- future clips
- continuity
- configured character names
- dialogue
- narration
- text on screen
- abstract explanations
- instructions to the video model
- explanations of why the idea is funny
- unnecessary camera directions

STYLE

End each prompt naturally with:

{style_suffix}

Do not add a generic cinematic sentence after the configured style.

{camera_instruction}

OUTPUT

Return exactly {count} concepts.

Use exactly this JSON structure:

[
    {{
        "title": "Short memorable title",
        "prompt": "Complete visual generation prompt"
    }}
]

Titles should be short, memorable, and directly connected to the visual idea.

Do not make every title follow the same naming pattern.

Return ONLY the JSON array.

No markdown.
No code block.
No explanation.
No commentary.

FINAL CHECK

Before returning the concepts, silently replace any idea that:

- is generic
- is difficult to understand visually
- requires dialogue or narration
- contains too many unrelated actions
- relies on random destruction
- copies another concept
- has weak visual curiosity
- depends on hidden backstory
- would be difficult for a video model to represent
- explains the joke instead of showing it

Prefer ideas with:

- strong first-frame curiosity
- one clear visual premise
- clear character behavior
- explicit spatial relationships when needed
- a memorable visual development
- a strong final visual moment
- simple, coherent physical action

Return exactly {count} concepts.
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

    def validate_prompt(
        self,
        prompt
    ):

        if not isinstance(
            prompt,
            str
        ):

            return False

        if not prompt.strip():

            return False

        return True

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