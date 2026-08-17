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

    def format_numbered(
        self,
        values
    ):

        if not isinstance(
            values,
            list
        ):

            return ""

        return "\n".join(
            f"{index}. {value}"
            for index, value in enumerate(
                values,
                start=1
            )
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

        comedy_structure = (
            self.prompt_config.get(
                "comedy_structure",
                []
            )
        )

        creative_priorities = (
            self.prompt_config.get(
                "creative_priorities",
                []
            )
        )

        action_guidance = (
            self.prompt_config.get(
                "action_guidance",
                []
            )
        )

        reaction_guidance = (
            self.prompt_config.get(
                "reaction_guidance",
                []
            )
        )

        environment_guidance = (
            self.prompt_config.get(
                "environment_guidance",
                []
            )
        )

        camera_guidance = (
            self.prompt_config.get(
                "camera_guidance",
                []
            )
        )

        payoff_types = (
            self.prompt_config.get(
                "payoff_types",
                []
            )
        )

        requirements = (
            self.prompt_config.get(
                "requirements",
                []
            )
        )

        prompt_format = (
            self.prompt_config.get(
                "prompt_format",
                {}
            )
        )

        clip_roles = (
            self.generation_config.get(
                "clip_roles",
                []
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

        clip_role_text = (
            "\n".join(
                f"- Clip {index}: {role}"
                for index, role in enumerate(
                    clip_roles,
                    start=1
                )
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
                40
            )
        )

        maximum_words = (
            prompt_format.get(
                "maximum_words",
                80
            )
        )

        chronological = (
            prompt_format.get(
                "chronological",
                True
            )
        )

        return f"""
Generate exactly {count} independent short-form vertical video concepts.

Each concept will be used directly as a text-to-video generation prompt.

There is NO continuity requirement between concepts. Each concept must work completely by itself. A character from one concept does not need to appear in another concept.

The creative goal is defined entirely by the configured category below.

GENRE:

{genre}

TONE:

{self.format_list(tone)}

WORLD:

{self.format_list(world)}

ALLOWED PROTAGONISTS:

{self.format_list(protagonists)}

COMEDY TYPES:

{self.format_list(comedy_types)}

GENERAL CONTENT RULES:

{self.format_bullets(rules)}

CREATIVE PRIORITIES:

{self.format_bullets(creative_priorities)}

COMEDY STRUCTURE:

{self.format_list(comedy_structure, " → ")}

ACTION GUIDANCE:

{self.format_bullets(action_guidance)}

REACTION GUIDANCE:

{self.format_bullets(reaction_guidance)}

ENVIRONMENT GUIDANCE:

{self.format_bullets(environment_guidance)}

CAMERA GUIDANCE:

{self.format_bullets(camera_guidance)}

CONFIGURED CAMERA STYLE:

{camera_style}

POSSIBLE PAYOFF TYPES:

{self.format_bullets(payoff_types)}

PROMPT REQUIREMENTS:

{self.format_bullets(requirements)}

CLIP VARIETY:

{clip_role_text}

When multiple concepts are requested, make them meaningfully different.

Vary the protagonist, situation, goal, environment, comedic mechanism, and type of payoff where appropriate.

Do not generate several versions of the same joke.

PROMPT FORMAT:

Write each prompt as exactly {paragraph_count} paragraph(s).

Each prompt should contain approximately {minimum_words}-{maximum_words} words.

Chronological visual progression: {chronological}.

The prompt should describe one coherent visual sequence rather than a traditional written story or multiple separate scenes.

The prompt should include:

{format_include}

The prompt must NOT include:

{format_exclude}

STYLE:

Every prompt MUST end with this configured style suffix:

{style_suffix}

OUTPUT:

Return exactly {count} concepts.

Every concept must use exactly this structure:

{{
    "title": "Short descriptive title",
    "prompt": "Complete text-to-video prompt"
}}

The title must be short and directly describe the visual premise.

Return ONLY the JSON array.

Do not include markdown.

Do not include a code block.

Do not include explanations.

Do not include commentary.

Before returning the JSON, internally verify every concept against the configured content rules and requirements.

Verify that:

- The requested number of concepts is present.
- Every concept has a valid configured protagonist type.
- Every protagonist is a living being or character-like creature.
- Every protagonist has a visible face.
- No inanimate object is the protagonist.
- The protagonist actively drives the action.
- Every concept has one central comedic premise.
- Every concept has a clear goal or intention.
- Every concept has one clear problem or obstacle.
- Every protagonist visibly reacts.
- Every concept has one natural escalation.
- Every concept has a visual payoff.
- The payoff relates directly to the central premise.
- The concepts are meaningfully varied.
- The prompts are visually coherent.
- The prompts do not depend on dialogue, narration, sound, or text.
- The configured style suffix appears at the end of every prompt.
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

            if not title or not prompt:

                continue

            prompts.append(
                {
                    "title": title,
                    "prompt": prompt
                }
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