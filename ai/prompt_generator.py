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

        requirements = (
            self.prompt_config.get(
                "requirements",
                []
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

        tone_text = (
            ", ".join(
                str(item)
                for item in tone
            )
        )

        world_text = (
            ", ".join(
                str(item)
                for item in world
            )
        )

        protagonist_text = (
            ", ".join(
                str(item)
                for item in protagonists
            )
        )

        comedy_type_text = (
            ", ".join(
                str(item)
                for item in comedy_types
            )
        )

        rule_text = (
            "\n".join(
                f"- {item}"
                for item in rules
            )
        )

        structure_text = (
            " → ".join(
                str(item)
                for item in comedy_structure
            )
        )

        requirement_text = (
            "\n".join(
                f"- {item}"
                for item in requirements
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

        style_parts = [
            visual_style,
            motion_style,
            camera_style
        ]

        style_suffix = (
            ", ".join(
                str(part).strip()
                for part in style_parts
                if str(part).strip()
            )
        )

        return f"""
Generate exactly {count} independent short-form vertical video concepts.

Each concept will be used directly as a text-to-video generation prompt.

The concepts will be combined into one short-form video, but the individual clips have NO continuity requirement. A character from one concept does not need to appear in another concept.

The goal is not random chaos.

The goal is CHARACTER-DRIVEN ABSURD COMEDY.

A viewer should immediately understand:

WHO is doing something,
WHAT they are trying to do,
WHAT simple problem they encounter,
HOW they react,
and WHY the final visual result is funny or surprising.

CREATIVE PRIORITY:

Character → Goal → Problem → Reaction → Escalation → Payoff

Use this structure as the underlying logic of every concept:

{structure_text}

GENRE:

{genre}

TONE:

{tone_text}

WORLD:

{world_text}

ALLOWED PROTAGONIST TYPES:

{protagonist_text}

The protagonist must be a living being or character-like creature with a visible face.

Inanimate objects can appear in the environment or be interacted with, but they must never be the protagonist or primary acting entity.

POSSIBLE COMEDY TYPES:

{comedy_type_text}

GENERAL CONTENT RULES:

{rule_text}

PROMPT REQUIREMENTS:

{requirement_text}

CLIP VARIETY:

When multiple clips are requested, deliberately vary the type of comedic experience.

Use these configured clip roles when available:

{clip_role_text}

Do not force these roles if they would produce weak ideas, but use them as a guide to make the final set feel varied.

Do not make all concepts involve running, crashing, falling, or chasing.

Mix different types of comedy such as:

- character behavior
- facial reaction
- awkward situations
- physical challenges
- misunderstandings
- absurd goals
- environmental interaction
- visual reveals
- unexpected consequences

Do not create four versions of the same joke.

RETENTION:

The first visual moment must already contain something interesting.

Do not begin with a character simply standing, walking normally, or waiting for something to happen.

The opening should immediately communicate the unusual situation, character behavior, or visual contradiction.

Create a curiosity gap naturally.

The viewer should want to know what happens to the character next.

Do not explain the joke to the viewer.

Let the visual situation communicate it.

CHARACTER:

Every concept must have one clear primary protagonist.

The protagonist must have:

- a recognizable physical appearance
- a visible face
- a readable emotional state
- a clear intention or goal
- physical interaction with the environment

The protagonist should drive the action.

Do not create a passive character while unrelated events happen around them.

COMEDY:

The humor should come primarily from the character's behavior, reaction, goal, mistake, misunderstanding, or situation.

Absurdity should support the premise rather than replace it.

Do not add random explosions, crashes, transformations, creatures, vehicles, or environmental destruction simply to increase intensity.

Every major event should logically follow from the central premise.

ACTION:

Use physical movement when it supports the idea.

Movement may include:

- running
- jumping
- sliding
- climbing
- grabbing
- struggling
- balancing
- hiding
- sneaking
- chasing
- escaping
- pushing
- pulling
- tumbling
- flying
- reacting

Do not force multiple actions into one concept.

One strong physical idea is better than a chain of unrelated actions.

ENVIRONMENT:

Use a simple, recognizable environment that helps communicate the joke.

The environment can create the problem, provide an obstacle, or amplify the character's reaction.

Avoid overly complicated environments that distract from the protagonist.

CAMERA:

Use camera movement only when it improves visual clarity or comedic timing.

Configured camera direction:

{camera_style}

Examples of useful camera behavior include:

- tracking the protagonist
- following movement
- pushing toward a reaction
- revealing the consequence
- pulling back for a visual reveal
- remaining relatively stable during facial comedy

Do not add random camera movements.

ESCALATION:

Use one natural escalation.

The situation should become slightly more difficult, surprising, embarrassing, or absurd.

Do not turn the escalation into a completely different event.

The escalation should come directly from the original premise.

PAYOFF:

End with a clear visual payoff.

The payoff can be:

- an unexpected result
- a character reaction
- a harmless failure
- an ironic outcome
- a visual reveal
- an absurd success
- an unexpected consequence

The ending should feel like the natural conclusion of the central joke.

VISUAL CLARITY:

Describe only what the video model needs to visualize.

Include:

- protagonist
- environment
- physical behavior
- facial reaction
- camera behavior
- escalation
- payoff

Use concrete nouns and physical verbs.

Avoid abstract explanations.

Do not explain why something is funny.

Do not require dialogue.

Do not require narration.

Do not require text on screen.

Do not rely on sound to communicate the joke.

PROMPT LENGTH:

Write each prompt as one chronological paragraph of roughly 40-80 words.

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

The prompt should describe one coherent visual sequence.

Do not write a traditional story.

Do not write multiple separate scenes.

Do not overload the prompt with unnecessary choreography.

STYLE:

Every prompt MUST end with the configured visual style:

{style_suffix}

IMPORTANT:

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

Before returning the JSON, internally verify:

- The requested number of concepts is present.
- Every concept has a clear protagonist.
- Every protagonist has a visible face.
- No inanimate object is the protagonist.
- Every concept is independent.
- Every concept has one central comedic premise.
- Every concept has a clear goal or intention.
- Every concept has a problem or obstacle.
- Every protagonist visibly reacts.
- Every concept has one natural escalation.
- Every concept has a visual payoff.
- The concepts are meaningfully varied.
- The prompts do not require dialogue or narration.
- The prompts do not depend on sound.
- The configured visual style appears at the end of every prompt.
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