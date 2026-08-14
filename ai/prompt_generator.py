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

These concepts will be converted directly into short text-to-video clips.

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

Each concept must describe a SINGLE continuous visual action that can be animated clearly over approximately 8 seconds.

The video must feel DYNAMIC and physically active from beginning to end.

Do NOT write prompts that mainly describe a static scene.

Do NOT simply describe an object sitting, standing, floating, spinning, changing appearance, or moving in place.

The subject should physically MOVE THROUGH THE ENVIRONMENT.

MOTION IS THE PRIORITY.

Every prompt should clearly communicate:

1. SUBJECT MOVEMENT
Describe what the main subject physically does.

Use strong action verbs such as:
runs, jumps, falls, slides, rolls, flies, swings, crashes, tumbles, races, bounces, launches, chases, collides, falls toward, rushes toward, moves past, flies across.

2. MOVEMENT DIRECTION
Clearly indicate where the subject moves.

Examples:
- across the room
- toward the camera
- away from the camera
- from left to right
- down a staircase
- through a doorway
- across a table
- upward into the air
- toward another object

3. CONTINUOUS MOTION
The action should continue throughout the clip.

Avoid prompts where most of the video would consist of a subject remaining in one position.

4. ENVIRONMENTAL INTERACTION
The moving subject should interact with objects or the environment whenever appropriate.

Examples:
- knocks something over
- bounces off a surface
- crashes into an object
- slides underneath something
- jumps over an obstacle
- sends objects flying
- pushes something across the floor
- causes a physical reaction

5. CAMERA MOTION
Include a simple camera movement that follows or emphasizes the action.

Examples:
- the camera tracks alongside the subject
- the camera follows from behind
- the camera pans rapidly with the movement
- the camera pushes toward the action
- the camera tilts downward as the subject falls
- the camera pulls back as the action escalates

The camera should feel active rather than completely stationary.

6. ESCALATION
The physical action should build toward a clear visual payoff.

The ending should be the most visually interesting moment.

7. VISUAL CLARITY
Describe only what should visibly happen.

Do not explain why something is funny.

Do not explain the concept.

Do not include abstract descriptions.

Do not include dialogue.

Do not require narration.

Do not require text on screen.

Do not rely on sound to make the action understandable.

8. SHORT-FORM VIDEO STRUCTURE

Think of each prompt as:

START:
The subject begins a physical action.

MOTION:
The subject continuously moves through the environment.

ESCALATION:
The movement becomes faster, larger, more chaotic, or more surprising.

PAYOFF:
The action ends with a strong visible physical event.

These are NOT separate scenes.

The entire concept must be one continuous visual sequence.

9. MOTION OVER TRANSFORMATION

Prefer physical movement over purely visual transformation.

Weak:
"A pencil transforms into a rainbow pencil."

Better:
"A pencil rolls rapidly down a hallway, launches off a small ramp into the air, crashes into a pencil sharpener, and shoots back out across the floor covered in rainbow shavings."

10. AVOID STATIC COMPOSITIONS

Avoid prompts like:

- "A character stands in a room while..."
- "An object sits on a table and..."
- "A creature looks at..."
- "Something floats in place..."
- "Something spins in place..."
- "Something changes into..."
- "Something suddenly becomes..."

Unless the subject is also clearly moving through the environment.

11. CAMERA AND SUBJECT MOVEMENT SHOULD WORK TOGETHER

Do not add random camera movement.

The camera should follow, reveal, emphasize, or react to the physical action.

For example:

"The camera tracks alongside the running subject, quickly pans as it jumps, then pushes toward the impact."

12. KEEP PROMPTS CONCISE

Each prompt should normally be one or two sentences.

Use concrete visual language.

Do not write a traditional story.

Do not create multiple separate scenes.

Do not reference previous or future clips.

Do not use recurring characters.

Do not use character names.

Do not require dialogue.

Do not require narration.

Prioritize:

- strong physical movement
- movement through space
- camera movement
- environmental interaction
- visual comedy
- absurdity
- unexpected physical behavior
- unusual scale
- surprising motion
- escalating action
- strong visual payoff

The final prompt should give a text-to-video model enough information to understand BOTH what is happening AND how everything is moving.

Return ONLY the JSON array.

Do not include markdown.

Do not include a code block.

Do not include an explanation.

Example:

[
    "A tiny elephant races across a crowded beach pushing an enormous beach ball, weaving between people as the camera tracks alongside it. The ball suddenly rolls downhill, dragging the elephant behind it before crashing into a stack of beach chairs.",
    "A vending machine violently rolls across a convenience store while the camera follows from behind, bouncing off shelves and sending drinks flying before crashing through the front doors.",
    "A giant rubber duck bounces rapidly through a miniature city, crushing through streets and launching over buildings as the camera pulls back to reveal the growing chaos."
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