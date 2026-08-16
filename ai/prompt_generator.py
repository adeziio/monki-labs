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

Each concept will be used directly as a text-to-video generation prompt.

There is NO required story continuity between separate concepts.

Each concept must be understandable as a complete visual idea on its own.

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

For every concept, return an object using exactly this structure:

{{
    "title": "Short descriptive title",
    "prompt": "Complete text-to-video prompt"
}}

The title should be short, descriptive, and directly related to the visual concept.

The prompt should describe a coherent visual sequence that can naturally continue for the configured video duration.

Do NOT assume a specific duration.

Do NOT mention seconds, frames, clip length, or timing instructions.

Do NOT create a traditional written story.

The video should feel like ONE coherent sequence rather than a list of unrelated events.

The model should have freedom to determine the exact subject, environment, physical behavior, and visual details.

MOTION:

Physical movement is important.

The main subject should generally move through the environment or cause visible physical interaction.

Prefer clear movement such as:

- running
- sliding
- rolling
- falling
- jumping
- flying
- swinging
- bouncing
- crashing
- tumbling
- racing
- chasing
- colliding
- launching
- moving through an environment

Do not force multiple different actions simply to make the prompt feel exciting.

A strong primary action with natural escalation is better than many unrelated actions.

ENVIRONMENTAL INTERACTION:

Whenever appropriate, allow the subject to interact with its surroundings.

Examples include:

- knocking objects over
- pushing objects
- bouncing off surfaces
- colliding with objects
- moving around obstacles
- causing nearby objects to react
- disturbing the environment
- creating a visible physical consequence

These interactions should naturally follow from the main action.

CAMERA:

Include simple camera behavior that supports the action.

Examples include:

- tracking the subject
- following from behind
- panning with movement
- moving toward the action
- pulling back to reveal the result
- tilting as the subject moves vertically
- reacting to a major impact

Do not use random camera movements.

The camera should help communicate the physical action clearly.

ESCALATION:

The visual situation should naturally become more interesting as the sequence progresses.

Escalation can come from:

- increasing speed
- increasing scale
- increasingly chaotic environmental interaction
- an unexpected obstacle
- an unexpected change in direction
- a larger physical consequence
- a surprising visual payoff

Do not force several unrelated events into the same prompt.

The ending should provide a clear visual payoff, but the entire sequence should still feel like one connected action.

VISUAL CLARITY:

The prompt should be easy for a video model to visualize.

Describe:

- what is visible
- what is moving
- where it is moving
- what it interacts with
- how the camera follows the action
- what visible consequence occurs

Do not explain why something is funny.

Do not explain the concept.

Do not include abstract descriptions.

Do not require dialogue.

Do not require narration.

Do not require text on screen.

Do not rely on sound for the visual action to make sense.

PROMPT LENGTH:

Keep the prompt concise.

Normally use one or two sentences.

Use enough detail for the video model to understand the sequence, but do not overload the prompt with unnecessary choreography.

Avoid long chains of actions connected with:

"then"

"and then"

"after that"

"followed by"

A prompt should generally focus on one primary physical idea with supporting environmental interactions.

WE WANT:

One clear visual action.

Movement through space.

Natural environmental interaction.

Simple camera movement.

Gradual escalation.

A strong visual payoff.

WE DO NOT WANT:

A sequence containing many unrelated actions.

A traditional story.

Multiple separate scenes.

A static composition.

A subject simply standing while things happen around it.

A subject performing many unrelated actions just because they sound exciting.
A static subject with no clear protagonist.
Slow setup before the action begins.

Do not reference previous or future concepts.

Do not require continuity between concepts.

Do not use configured character names.

Do not require dialogue.

Do not require narration.

Prioritize:

- visual comedy
- absurdity
- physical movement
- unusual situations
- unexpected behavior
- environmental interaction
- surprising scale
- escalating physical consequences
- clear visual storytelling
- strong visual payoff
- a clear character or animal protagonist
- immediate action that hooks in the first frame

The concept should remain visually coherent even if the video generation model decides to introduce natural camera movement or scene changes.

Return ONLY the JSON array.

Do not include markdown.

Do not include a code block.

Do not include an explanation.

Example:

[
    {{
        "title": "Runaway Shopping Cart",
        "prompt": "A shopping cart races uncontrollably through a crowded supermarket aisle, weaving around displays and knocking items loose as the camera tracks alongside it before the cart launches through the automatic doors and crashes into a towering display outside."
    }},
    {{
        "title": "Giant Balloon Escape",
        "prompt": "A giant balloon breaks free inside a busy warehouse and drifts rapidly through the aisles, dragging loose objects behind it as workers scatter and the camera follows its unpredictable path before it bursts through the roof."
    }},
    {{
        "title": "Cat vs. Gravity",
        "prompt": "A house cat discovers it can stick to the ceiling and walk upside down, then uses this to chase a laser pointer dot across the kitchen cabinets and fridge as the camera tilts and pans to follow its impossible path before it finally crashes down into a pile of spilled cereal."
    }}
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
                dict
            ):

                continue

            title = item.get(
                "title",
                ""
            )

            prompt = item.get(
                "prompt",
                ""
            )

            title = str(
                title
            ).strip()

            prompt = str(
                prompt
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