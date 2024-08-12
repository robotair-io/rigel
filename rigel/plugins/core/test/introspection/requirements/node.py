from rigel.plugins.core.test.introspection.command import CommandHandler


class SimulationRequirementNode(CommandHandler):
    """
    Handles commands related to simulation requirements and keeps track of the
    satisfaction status of each requirement, represented by a boolean flag `satisfied`.

    Attributes:
        satisfied (bool): Initialized to False by default. It indicates whether
            or not a specific requirement within a simulation has been fulfilled.

    """
    # All simulation requirements nodes have a flag
    # that indicates whether or not that requirement was satisfied.
    satisfied: bool = False
