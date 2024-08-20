from pydantic import BaseModel, Extra, validator
from rigel.exceptions import UnsupportedPlatformError
from typing import Dict, List


SUPPORTED_PLATFORMS: List[str] = [
    'linux/amd64',
    'linux/arm64',
]


class PluginModel(BaseModel, extra=Extra.forbid):
    """
    Defines a model with required and optional fields, including image, tags,
    force_tag_latest, buildargs, load, platforms, and push. The `validate_platforms`
    method ensures that the provided platform values are supported by checking
    them against the `SUPPORTED_PLATFORMS` list.

    Attributes:
        image (str): Required to be set when creating an instance of this class,
            meaning it cannot be left blank or null.
        tags (List[str]): Initialized with a default value ['latest']. This means
            that if no tags are specified when creating an instance of `PluginModel`,
            it will have 'latest' as its only tag.
        force_tag_latest (bool): Optional. Its presence does not affect the
            validation of other attributes, but it can be used to control some
            behavior related to tags when creating or updating a plugin.
        buildargs (Dict[str, str]): Initialized with an empty dictionary. It
            represents a collection of key-value pairs where both keys and values
            are strings.
        load (bool): Optional. It defaults to False, indicating whether or not to
            load the plugin during execution.
        platforms (List[str]): Optional by default. It represents a list of platform
            names that are supported by this plugin. The value for this field
            defaults to an empty list if not provided.
        push (bool): Set to False by default. This indicates whether a push operation
            should be performed for the plugin or not.

    """

    # Required fields.
    image: str

    # Optional fields.
    tags: List[str] = ['latest']
    force_tag_latest: bool = True
    buildargs: Dict[str, str] = {}
    load: bool = False
    platforms: List[str] = []
    push: bool = False

    @validator('platforms')
    def validate_platforms(cls, platforms: List[str]) -> List[str]:
        """
        Validates a list of platform names against a set of supported platforms.
        If an unsupported platform is found, it raises an UnsupportedPlatformError;
        otherwise, it returns the validated list of platforms.

        Args:
            platforms (List[str]): Expected to contain one or more strings
                representing platform names. These platform names are subject to
                validation against the list of supported platforms.

        Returns:
            List[str]: The input list 'platforms' after validation. It filters out
            any unsupported platforms, and if all platforms are supported, it
            returns the original list.

        """
        supported_platforms = [p for p in SUPPORTED_PLATFORMS]
        for platform in platforms:
            if platform not in supported_platforms:
                raise UnsupportedPlatformError(platform)
        return platforms
