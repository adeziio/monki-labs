import json

from ai.base_ai_service import BaseAIService
from ai.providers.ollama_provider import OllamaProvider


class StoryGenerator(BaseAIService):

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

        self.character_manager = (
            config["character_manager"]
        )

        self.active_series = (
            config["series"]["active_series"]
        )

        self.series_config = (
            config["series"]["series"]
            [self.active_series]
        )

    def generate(
        self,
        previous_stories=None
    ):

        self.log(
            "Generating visual comedy story"
        )

        if previous_stories is None:

            previous_stories = []

        main_character_id = (
            self.character_manager
            .get_main_character_id(
                self.active_series
            )
        )

        available_character_ids = (
            self.character_manager
            .get_character_ids_for_series(
                self.active_series
            )
        )

        characters_prompt = (
            self.build_characters_prompt(
                available_character_ids
            )
        )

        previous_stories_prompt = (
            self.build_previous_stories_prompt(
                previous_stories
            )
        )

        series_prompt = (
            self.build_series_prompt()
        )

        character_ids_prompt = (
            self.build_character_ids_prompt(
                available_character_ids
            )
        )

        output_structure_prompt = (
            self.build_output_structure_prompt(
                available_character_ids,
                main_character_id
            )
        )

        prompt = self.build_prompt(
            series_prompt,
            characters_prompt,
            character_ids_prompt,
            main_character_id,
            previous_stories_prompt,
            output_structure_prompt
        )

        response = self.llm.generate(
            prompt
        )

        story = self.parse_response(
            response,
            main_character_id,
            available_character_ids
        )

        if story is None:

            self.log(
                "Story generation failed validation."
            )

            return None

        return story

    def build_prompt(
        self,
        series_prompt,
        characters_prompt,
        character_ids_prompt,
        main_character_id,
        previous_stories_prompt,
        output_structure_prompt
    ):

        return f"""
        Create ONE episode for the configured series.

        The episode will eventually become a short animated video.

        The story is NOT the final video.

        The story will first be converted into generated images.

        Each generated image will then become the visual starting state
        for a short animation beat.

        Therefore, every scene must be designed specifically to make:

        STORY -> IMAGE -> ANIMATION

        work naturally.

        ============================================================
        SERIES CONFIGURATION
        ============================================================

        {series_prompt}

        ============================================================
        AVAILABLE CHARACTERS
        ============================================================

        {characters_prompt}

        ============================================================
        VALID CHARACTER IDs
        ============================================================

        {character_ids_prompt}

        ============================================================
        MAIN CHARACTER
        ============================================================

        {main_character_id}

        ============================================================
        PREVIOUS EPISODES
        ============================================================

        {previous_stories_prompt}

        ============================================================
        STORY GOAL
        ============================================================

        Create a simple visual comedy story that follows the configured
        series genre, tone, world, character personalities, behavior rules,
        story rules, and episode structure.

        The story must be understandable without dialogue or narration.

        The comedy should come primarily from physical actions,
        consequences, timing, mistakes, collisions, movement, objects,
        environmental interactions, and escalating situations.

        The story should be simple enough that every scene can be represented
        clearly in a single generated image.

        ============================================================
        STORY STRUCTURE
        ============================================================

        The story must follow these four phases in order:

        1. Hook
        2. Setup
        3. Escalation
        4. Ending

        These are STORY PHASES, not scene counts.

        Do NOT force the story into four scenes.

        Multiple scenes may belong to the same phase.

        The number of scenes should naturally emerge from the number of
        animation-friendly physical beats required to tell the story.

        All four phases must be represented.

        The phases must remain in this order.

        Once the story progresses into Escalation, do not return to Setup.

        Once the story reaches Ending, do not return to Escalation.

        ============================================================
        ANIMATION-FRIENDLY SCENE DESIGN
        ============================================================

        THIS IS ONE OF THE MOST IMPORTANT RULES.

        Each scene will become ONE SHORT ANIMATION BEAT.

        Therefore:

        ONE SCENE = ONE DISCRETE PHYSICAL EVENT.

        The action should describe one physical event that could reasonably
        happen during one short continuous animation.

        The scene should have:

        - one primary physical action
        - one clear physical state
        - one obvious visual result
        - one simple animation opportunity

        Do not combine multiple sequential actions into one scene.

        ============================================================
        ACTION CHAIN SPLITTING
        ============================================================

        If an action contains multiple sequential physical events,
        split them into separate scenes.

        For example, if a character:

        climbs
        slips
        falls
        lands

        those should be separate animation beats.

        Do NOT write:

        "maxmonkey climbs a tree, slips, and falls"

        Instead create separate scenes for:

        "maxmonkey climbs the tree"

        "maxmonkey slips from the tree"

        "maxmonkey falls from the tree"

        "maxmonkey lands in leaves"

        Each event receives its own visual state and animation opportunity.

        Another example:

        If a character:

        runs toward another character
        grabs the character
        pulls the character
        falls with the character

        these are multiple physical events.

        Do not combine them.

        ============================================================
        ONE BEAT, NOT ONE VERB
        ============================================================

        Do not interpret this rule as simply counting verbs.

        The goal is NOT:

        "one verb per scene"

        The goal is:

        "one visually distinct physical beat per scene"

        A single physical event may contain wording that describes its
        immediate physical result.

        For example:

        "maxmonkey falls into a pile of leaves"

        is one physical event.

        But:

        "maxmonkey falls into leaves and rolls across the ground"

        contains two distinct physical events and should be split.

        ============================================================
        PHYSICAL BEAT QUALITY
        ============================================================

        Prefer actions that are:

        - concrete
        - physical
        - visually obvious
        - easy to pose
        - easy to animate
        - easy to understand without dialogue
        - connected to the previous scene
        - useful as a generated image
        - useful as an animation starting state

        Good physical beats include:

        - climbing
        - jumping
        - falling
        - slipping
        - tripping
        - grabbing
        - dropping
        - rolling
        - swinging
        - colliding
        - bumping
        - pulling
        - pushing
        - catching
        - landing
        - knocking something over
        - stepping on an object
        - getting stuck
        - becoming trapped by an object
        - an object falling
        - an object rolling
        - an object breaking
        - an object bouncing
        - an object knocking into another object

        Avoid abstract or weak actions such as:

        - laughs
        - smiles
        - reacts
        - gets surprised
        - becomes confused
        - feels scared
        - feels embarrassed
        - prepares to fall
        - tries to do something
        - thinks about something
        - notices something

        These do not provide strong enough physical information for
        image-to-animation generation.

        If a character's emotional reaction is important, express it through
        a concrete physical action instead.

        ============================================================
        CAUSE AND EFFECT
        ============================================================

        The episode should behave like a continuous physical chain.

        Prefer:

        action
        ->
        consequence
        ->
        reaction
        ->
        new consequence
        ->
        escalation
        ->
        resolution

        Each scene should naturally lead into the next.

        For example:

        maxmonkey steps on a loose branch
        ->
        the branch bends
        ->
        maxmonkey slips
        ->
        maxmonkey falls
        ->
        sidsquirrel grabs maxmonkey
        ->
        sidsquirrel loses balance
        ->
        both characters fall
        ->
        lialynx catches sidsquirrel
        ->
        maxmonkey lands safely

        This is only an illustration of the type of causal structure desired.

        Do not copy these exact actions.

        Create an original story appropriate for the configured series.

        ============================================================
        CONTINUOUS PHYSICAL STATE
        ============================================================

        Preserve important physical state from scene to scene.

        If a character is falling, the next scene should logically continue
        or affect that fall.

        If an object has been dropped, its later movement can become part of
        the ongoing situation.

        If a character has become stuck, the next scene should deal with
        that situation rather than suddenly introducing an unrelated event.

        If an object has knocked something over, the resulting movement or
        consequence should be usable by later scenes.

        The audience should be able to understand what happened simply by
        watching the sequence of images.

        ============================================================
        VISUAL IMAGE REQUIREMENT
        ============================================================

        Every action must be representable as a strong single image.

        The image should clearly communicate:

        - who is acting
        - what physical event is happening
        - what object or environment is involved
        - the important physical relationship between characters and objects

        Avoid actions that require several moments of time to understand.

        Avoid actions that require invisible information.

        Avoid actions that depend on dialogue or narration.

        ============================================================
        ANIMATION TRANSITION REQUIREMENT
        ============================================================

        Each scene should have a natural relationship to the previous and
        next scene.

        The generated image for scene N should make sense as the starting
        visual state for the animation of scene N.

        The resulting animation should naturally transition toward scene N+1.

        Avoid scene changes that require impossible or unexplained physical
        transitions.

        Avoid introducing completely new situations between consecutive scenes.

        ============================================================
        CHARACTER IDENTIFIERS
        ============================================================

        The VALID CHARACTER IDs section contains the ONLY character IDs
        allowed in the story.

        Copy those IDs exactly.

        Never invent character IDs.

        Never rename character IDs.

        Never abbreviate character IDs.

        Never replace character IDs with generic labels.

        Never use placeholders.

        NEVER output identifiers such as:

        character_a
        character_b
        character_c
        char_001
        char_002
        char_003
        character_id
        main_character_id
        supporting_character_id

        Those identifiers are NOT valid.

        Every character mentioned in any action must use an exact ID from
        the VALID CHARACTER IDs section.

        ============================================================
        CHARACTER USAGE
        ============================================================

        The top-level "characters" dictionary defines every character
        participating in the episode.

        Every participating character must appear exactly once.

        The main character must always have the role "main".

        All other participating characters must have the role "supporting".

        Every character mentioned in an action must appear in the
        top-level "characters" dictionary.

        Do not mention characters that are not participating.

        Do not create a characters field inside individual scenes.

        ============================================================
        ACTION FIELD
        ============================================================

        The "action" field is the ONLY scene-level visual instruction.

        Every action must describe only the physical event visible in that
        scene.

        Every physically acting character must be explicitly identified by
        their exact runtime character ID.

        Every character physically affected by an action must be explicitly
        identified by their exact runtime character ID.

        Do not use ambiguous references such as:

        they
        them
        their
        everyone
        both
        all of them
        the characters
        the group
        the others

        Do not describe character appearance.

        Do not describe camera directions.

        Do not describe animation instructions.

        Do not describe sound.

        Do not describe music.

        Do not describe dialogue.

        Keep actions short and direct.

        ============================================================
        CHARACTER PERSONALITY
        ============================================================

        Actions should naturally reflect the personalities and behavior
        rules provided for each character.

        Character personality should influence WHAT characters do,
        not be written as abstract personality descriptions inside actions.

        ============================================================
        UNIQUENESS
        ============================================================

        Review previous episodes.

        Do not simply replace the object from a previous episode.

        Avoid repeating the same underlying comedy mechanism.

        Prefer a meaningfully different physical-comedy mechanism when possible.

        Keep the new story simple.

        ============================================================
        OUTPUT
        ============================================================

        Return ONLY valid JSON.

        Do not include markdown.

        Do not include explanations.

        {output_structure_prompt}

        Scene numbers must begin at 1 and increase sequentially.

        The number of scenes is flexible.

        Multiple scenes may share the same story phase.

        ============================================================
        FINAL CHECK
        ============================================================

        Before returning JSON, verify all of the following:

        - output is valid JSON only
        - at least one scene exists
        - all four story phases are represented
        - purposes follow:
          Hook -> Setup -> Escalation -> Ending
        - scene numbers begin at 1
        - scene numbers increase sequentially
        - the main character is included
        - the main character has role "main"
        - all other participating characters have role "supporting"
        - every character ID is an exact runtime character ID
        - no invented character IDs exist
        - no placeholder character IDs exist
        - no char_001 or similar identifiers exist
        - every character mentioned in an action appears in "characters"
        - one central situation connects the episode
        - each scene logically follows the previous scene
        - physical cause and effect are preserved
        - each scene represents one discrete physical beat
        - sequential physical events are split into separate scenes
        - unrelated physical actions are not combined
        - trivial movements are not unnecessarily split
        - each action can be represented clearly in one generated image
        - each action can be animated as one short continuous beat
        - actions are concrete and physical
        - actions do not rely on dialogue or narration
        - no ambiguous character references appear
        - no character appearance descriptions appear
        - no camera directions appear
        - no animation instructions appear
        - no sound or music instructions appear
        - no scene contains a redundant character list
        - no field is blank
        """

    def build_series_prompt(
        self
    ):

        return json.dumps(
            self.series_config,
            indent=2
        )

    def build_character_ids_prompt(
        self,
        character_ids
    ):

        if not character_ids:

            return "No valid character IDs are available."

        lines = []

        for character_id in character_ids:

            lines.append(
                f"- {character_id}"
            )

        return "\n".join(
            lines
        )

    def build_output_structure_prompt(
        self,
        available_character_ids,
        main_character_id
    ):

        character_entries = []

        for character_id in available_character_ids:

            if character_id == main_character_id:

                role = "main"

            else:

                role = "supporting"

            character_entries.append(
                f'            "{character_id}": "{role}"'
            )

        characters_json = ",\n".join(
            character_entries
        )

        return f"""
        Use exactly this JSON structure:

        {{
            "characters": {{
{characters_json}
            }},
            "scenes": [
                {{
                    "scene": 1,
                    "purpose": "Hook",
                    "action": ""
                }},
                {{
                    "scene": 2,
                    "purpose": "Hook",
                    "action": ""
                }},
                {{
                    "scene": 3,
                    "purpose": "Setup",
                    "action": ""
                }}
            ]
        }}

        The character dictionary above shows the actual runtime character IDs.

        Only include characters that actually participate in the episode.

        If a character does not participate, remove that character from the
        dictionary.

        Do not add any character that is not listed in the VALID CHARACTER IDs.

        The example contains three scene slots only to demonstrate formatting.
        It does NOT define the required number of scenes.

        Add or remove scenes as needed.

        The final story should contain exactly as many scenes as necessary
        to represent the complete sequence of animation-friendly physical beats.
        """

    def build_characters_prompt(
        self,
        character_ids
    ):

        descriptions = []

        for character_id in character_ids:

            character = (
                self.character_manager
                .get_character(
                    character_id
                )
            )

            descriptions.append(
                json.dumps(
                    {
                        "id": character_id,
                        "trigger_word":
                            self.character_manager
                            .get_trigger_word(
                                character_id
                            ),
                        "role": character.get(
                            "role",
                            ""
                        ),
                        "species": character.get(
                            "species",
                            ""
                        ),
                        "importance": character.get(
                            "importance",
                            ""
                        ),
                        "personality": (
                            self.character_manager
                            .get_personality(
                                character_id
                            )
                        ),
                        "behavior_rules": (
                            self.character_manager
                            .get_behavior_rules(
                                character_id
                            )
                        ),
                        "story_rules": (
                            self.character_manager
                            .get_story_rules(
                                character_id
                            )
                        )
                    },
                    indent=2
                )
            )

        return "\n\n".join(
            descriptions
        )

    def build_previous_stories_prompt(
        self,
        stories
    ):

        if not stories:

            return (
                "No previous episodes. "
                "Create a fresh premise."
            )

        summaries = []

        for item in stories:

            if not isinstance(
                item,
                dict
            ):

                continue

            story = (
                item.get(
                    "story",
                    {}
                )
            )

            if not isinstance(
                story,
                dict
            ):

                continue

            scenes = (
                story.get(
                    "scenes",
                    []
                )
            )

            scene_summaries = []

            if isinstance(
                scenes,
                list
            ):

                for scene in scenes:

                    if not isinstance(
                        scene,
                        dict
                    ):

                        continue

                    scene_summaries.append(
                        {
                            "purpose":
                                scene.get(
                                    "purpose",
                                    ""
                                ),
                            "action":
                                scene.get(
                                    "action",
                                    ""
                                )
                        }
                    )

            summaries.append(
                json.dumps(
                    {
                        "characters":
                            story.get(
                                "characters",
                                {}
                            ),
                        "scenes":
                            scene_summaries
                    },
                    indent=2
                )
            )

        if not summaries:

            return (
                "No previous episodes. "
                "Create a fresh premise."
            )

        return "\n\n".join(
            summaries
        )

    def parse_response(
        self,
        response,
        main_character_id,
        available_character_ids
    ):

        try:

            data = json.loads(
                response
            )

            if not isinstance(
                data,
                dict
            ):

                raise ValueError(
                    "Response is not a JSON object."
                )

            cleaned = {
                "characters":
                    self.normalize_characters(
                        data.get(
                            "characters"
                        ),
                        main_character_id,
                        available_character_ids
                    ),
                "scenes":
                    self.normalize_scenes(
                        data.get(
                            "scenes"
                        )
                    )
            }

            self.validate_story(
                cleaned,
                main_character_id,
                available_character_ids
            )

            return cleaned

        except json.JSONDecodeError as error:

            self.log(
                f"AI returned invalid JSON: {error}"
            )

            return None

        except (
            ValueError,
            TypeError
        ) as error:

            self.log(
                f"Story validation failed: {error}"
            )

            return None

    def validate_story(
        self,
        story,
        main_character_id,
        available_character_ids
    ):

        scenes = story.get(
            "scenes",
            []
        )

        if not isinstance(
            scenes,
            list
        ) or not scenes:

            raise ValueError(
                "Story must contain at least one scene."
            )

        story_characters = story.get(
            "characters",
            {}
        )

        if not isinstance(
            story_characters,
            dict
        ):

            raise ValueError(
                "Characters must be a dictionary."
            )

        if (
            not main_character_id
            or
            main_character_id
            not in story_characters
        ):

            raise ValueError(
                "Main character missing from story."
            )

        for character_id, role in (
            story_characters.items()
        ):

            if character_id not in (
                available_character_ids
            ):

                raise ValueError(
                    "Invalid character ID."
                )

            if role not in (
                "main",
                "supporting"
            ):

                raise ValueError(
                    "Invalid character role."
                )

        if story_characters.get(
            main_character_id
        ) != "main":

            raise ValueError(
                "Main character must have "
                "the main role."
            )

        expected_purposes = [
            "Hook",
            "Setup",
            "Escalation",
            "Ending"
        ]

        phase_indexes = {
            purpose: index
            for index, purpose in enumerate(
                expected_purposes
            )
        }

        previous_phase_index = -1

        phase_counts = {
            purpose: 0
            for purpose in expected_purposes
        }

        for index, scene in enumerate(
            scenes
        ):

            if not isinstance(
                scene,
                dict
            ):

                raise ValueError(
                    "Invalid scene."
                )

            if scene.get(
                "scene"
            ) != index + 1:

                raise ValueError(
                    "Invalid scene number."
                )

            purpose = scene.get(
                "purpose"
            )

            if purpose not in phase_indexes:

                raise ValueError(
                    "Invalid scene purpose."
                )

            current_phase_index = (
                phase_indexes[purpose]
            )

            if current_phase_index < (
                previous_phase_index
            ):

                raise ValueError(
                    "Scene purposes must follow "
                    "the configured episode structure."
                )

            previous_phase_index = (
                current_phase_index
            )

            phase_counts[purpose] += 1

            if "characters" in scene:

                raise ValueError(
                    "Scenes must not contain "
                    "a characters field."
                )

            if not scene.get(
                "action"
            ):

                raise ValueError(
                    "Scene action is blank."
                )

        for purpose in expected_purposes:

            if phase_counts[purpose] == 0:

                raise ValueError(
                    "Story must contain all "
                    "four episode phases."
                )

    def normalize_text(
        self,
        value
    ):

        if not isinstance(
            value,
            str
        ):

            return ""

        return value.strip()

    def normalize_characters(
        self,
        characters,
        main_character_id,
        available_character_ids
    ):

        if not isinstance(
            characters,
            dict
        ):

            characters = {}

        normalized = {}

        for character_id, role in (
            characters.items()
        ):

            if (
                not isinstance(
                    character_id,
                    str
                )
                or
                character_id
                not in available_character_ids
            ):

                continue

            if role not in (
                "main",
                "supporting"
            ):

                continue

            if character_id not in normalized:

                normalized[
                    character_id
                ] = role

        if (
            main_character_id
            and
            main_character_id
            not in normalized
        ):

            normalized = {
                main_character_id:
                    "main",
                **normalized
            }

        elif (
            main_character_id
            and
            normalized.get(
                main_character_id
            ) != "main"
        ):

            normalized[
                main_character_id
            ] = "main"

        return normalized

    def normalize_scenes(
        self,
        scenes
    ):

        if not isinstance(
            scenes,
            list
        ):

            return []

        normalized = []

        valid_purposes = {
            "Hook",
            "Setup",
            "Escalation",
            "Ending"
        }

        for scene in scenes:

            if not isinstance(
                scene,
                dict
            ):

                continue

            action = (
                self.normalize_text(
                    scene.get(
                        "action"
                    )
                )

            )

            purpose = (
                self.normalize_text(
                    scene.get(
                        "purpose"
                    )
                )
            )

            if not action:

                continue

            if purpose not in valid_purposes:

                continue

            normalized.append(
                {
                    "scene":
                        len(normalized) + 1,
                    "purpose":
                        purpose,
                    "action":
                        action
                }
            )

        return normalized

    def build_safe_fallback(
        self,
        main_character_id
    ):

        return {
            "characters": {
                main_character_id:
                    "main"
            }
            if main_character_id
            else {},
            "scenes": []
        }