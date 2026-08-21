import json
import math
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

        content_config = config["content"]

        active_category = (
            content_config["active_category"]
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

        self.recent_concepts = []

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

    def get_significant_words(self, value):

        ignored = {
            "a", "an", "the", "and", "as", "at", "by", "from",
            "in", "into", "of", "on", "or", "that", "then", "to",
            "with", "while", "suddenly", "tiny", "small", "normal",
            "sits", "standing", "near"
        }

        words = re.findall(
            r"[a-z0-9]+",
            str(value).lower()
        )

        return {
            word
            for word in words
            if len(word) > 3 and word not in ignored
        }

    def is_repetitive_concept(
        self,
        title,
        prompt,
        history=None
    ):

        current_title = self.get_significant_words(
            title
        )

        current_prompt = self.get_significant_words(
            prompt
        )

        motif_terms = set(
            self.prompt_config.get(
                "repetition_motif_terms",
                []
            )
        )

        current_motifs = {
            term
            for term in current_prompt
            if term in motif_terms
        }

        previous_concepts = (
            history
            if history is not None
            else self.recent_concepts
        )

        for previous in previous_concepts:

            previous_title = self.get_significant_words(
                previous["title"]
            )

            previous_prompt = self.get_significant_words(
                previous["prompt"]
            )

            if title.strip().casefold() == previous["title"].strip().casefold():

                return True, "duplicate title"

            title_overlap = current_title & previous_title

            if (
                current_title and
                len(title_overlap) >= max(
                    2,
                    math.ceil(
                        len(current_title) * 0.65
                    )
                )
            ):

                return True, "high title overlap"

            motif_overlap = current_motifs & {
                term
                for term in previous_prompt
                if term in motif_terms
            }

            if len(motif_overlap) >= 2:

                return True, (
                    "repeated motif: "
                    + ", ".join(
                        sorted(motif_overlap)
                    )
                )

            prompt_overlap = current_prompt & previous_prompt

            if (
                len(prompt_overlap) >= 5 and
                len(prompt_overlap) /
                max(
                    len(current_prompt),
                    1
                ) >= 0.65
            ):

                return True, "high prompt overlap"

        return False, ""

    def validate_visual_prompt(self, prompt):

        normalized = str(
            prompt
        ).strip().casefold()

        forbidden_phrases = {
            str(value).strip().casefold()
            for value in self.prompt_config.get(
                "quality_forbidden_phrases",
                []
            )
            if str(value).strip()
        }

        for phrase in forbidden_phrases:

            if phrase in normalized:

                return False, (
                    f"abstract or unsafe phrase: {phrase}"
                )

        action_markers = self.prompt_config.get(
            "quality_action_markers",
            []
        )

        action_count = sum(
            normalized.count(
                str(marker).casefold()
            )
            for marker in action_markers
        )

        maximum_actions = int(
            self.prompt_config.get(
                "quality_max_action_markers",
                5
            )
        )

        if action_count > maximum_actions:

            return False, (
                f"too many simultaneous actions ({action_count})"
            )

        clause_markers = (
            " while ",
            " as ",
            " then ",
            " and "
        )

        clause_count = sum(
            normalized.count(
                marker
            )
            for marker in clause_markers
        )

        maximum_clauses = int(
            self.prompt_config.get(
                "quality_max_clause_markers",
                3
            )
        )

        if clause_count > maximum_clauses:

            return False, (
                f"too many chained clauses ({clause_count})"
            )

        absurdity_markers = {
            str(value).strip().casefold()
            for value in self.prompt_config.get(
                "visual_absurdity_markers",
                []
            )
            if str(value).strip()
        }

        physics_only_markers = {
            str(value).strip().casefold()
            for value in self.prompt_config.get(
                "boring_physics_markers",
                []
            )
            if str(value).strip()
        }

        has_absurdity_marker = any(
            marker in normalized
            for marker in absurdity_markers
        )

        has_physics_only_marker = any(
            marker in normalized
            for marker in physics_only_markers
        )

        if (
            has_physics_only_marker and
            not has_absurdity_marker
        ):

            return False, (
                "generic physics spectacle without a visual absurdity hook"
            )

        return True, ""

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

        instructions = (
            self.prompt_config.get(
                "instructions",
                []
            )
        )

        creative_directions = (
            self.prompt_config.get(
                "creative_directions",
                []
            )
        )

        priorities = (
            self.prompt_config.get(
                "creative_priorities",
                []
            )
        )

        diversity = (
            self.prompt_config.get(
                "diversity_guidance",
                []
            )
        )

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

        candidate_pool_size = int(
            self.prompt_config.get(
                "candidate_pool_size",
                5
            )
        )

        return f"""
Generate exactly {count} final original video concepts.

For every final concept, silently brainstorm at least
{candidate_pool_size} different candidates first. Reject candidates that
are generic, abstract, overloaded, repetitive, or difficult to render.
Output only the strongest surviving concepts.

GENRE
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

PROMPT LENGTH

Write each prompt in approximately {minimum_words}-{maximum_words} words.
This range is derived from the configured video duration of
approximately {duration_seconds:g} seconds.

Each prompt must describe ONE tightly framed but aggressively bizarre visual event
suitable for an approximately {duration_seconds:g}-second vertical video.

Use this exact visual structure:
ordinary recognizable setup → one impossible physical mutation or behavior →
one immediate escalation → one concrete final image

Keep the action concrete and easy to visualize, but make the underlying situation
irrational, surreal, cursed, or gloriously stupid.

Do not write a normal wholesome scene, generic cartoon gag, ordinary slapstick,
or predictable animal behavior.

The prompt may contain a rapid setup, transformation, and payoff if they form
one continuous visual gag.

Prefer a strong visual contradiction: an impossible object, an inappropriate job,
a creature behaving like a bureaucrat, a tiny world inside a normal object, or
a mundane situation obeying a ridiculous rule.

Make the first image immediately strange. Escalate once. End on the most
unexpected clear visual consequence.

Favor concepts that feel like an original internet fever dream rather than
polished fantasy, conventional comedy, or a children's cartoon.

Use specific nouns and physical verbs. Avoid vague adjectives such as "funny,"
"weird," "crazy," or "interesting" unless paired with a concrete visual action.

Every concept in this batch must use a different dominant absurdity family,
protagonist type, setting, or payoff whenever possible.

Do not make every concept an office, bureaucrat, miniature society, meeting,
paperwork, or authority figure. Rotate radically between food, animals,
household objects, public spaces, creatures, anatomy, and bizarre jobs.

The absurdity must be visible in the first image or first physical action.
Prefer "a spoon grows legs and sprints" over "a spoon floats" or "gravity breaks."

Do not use an abstract world-ending consequence. Show one object physically
changing, moving, opening, growing, walking, escaping, or behaving incorrectly.

Do not mention duration, seconds, frames, timing instructions, dialogue,
narration, previous clips, future clips, or instructions to the video model.

Let the concept determine the number of characters and objects.

OUTPUT

Return exactly {count} concepts.

Use exactly this JSON structure:

[
    {{
        "title": "Short memorable title",
        "prompt": "Short visual generation prompt"
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

        prompt = self.build_prompt(
            count
        )

        for attempt in range(2):

            response = self.llm.generate(
                prompt,
                response_format=self.get_response_schema()
            )

            prompts = self.parse_response(
                response,
                count
            )

            if prompts or attempt == 1:

                return prompts

            self.log(
                "No fresh concepts survived validation. "
                "Requesting a diversity retry."
            )

            prompt = self.build_prompt(
                count
            )

        return []

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

            visually_valid, reason = self.validate_visual_prompt(
                prompt
            )

            if not visually_valid:

                self.log(
                    f"Skipping '{title}' because it is difficult "
                    f"to film clearly ({reason})."
                )

                continue

            repetitive, reason = self.is_repetitive_concept(
                title,
                prompt
            )

            if repetitive:

                self.log(
                    f"Skipping '{title}' because it repeats "
                    f"a recent concept ({reason})."
                )

                continue

            repetitive, reason = self.is_repetitive_concept(
                title,
                prompt,
                history=self.recent_concepts + prompts
            )

            if repetitive:

                self.log(
                    f"Skipping '{title}' because it repeats "
                    f"a recent concept ({reason})."
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
