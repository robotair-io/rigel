from hpl.parser import property_parser
from hpl.visitor import (
    HplAstVisitor,
    HplEvent,
    HplEventDisjunction,
    HplPattern,
    HplSimpleEvent,
    HplVacuousTruth
)
from typing import Optional
from .callback import CallbackGenerator
from .requirements import (
    AbsenceSimulationRequirementNode,
    DisjointSimulationRequirementNode,
    ExistenceSimulationRequirementNode,
    PreventionSimulationRequirementNode,
    RequirementSimulationRequirementNode,
    ResponseSimulationRequirementNode,
    SimpleSimulationRequirementNode,
    SimulationRequirementNode
)


class SimulationRequirementsVisitor(HplAstVisitor):
    """
    Traverses an abstract syntax tree (AST) and extracts simulation requirements
    from it, creating a hierarchical structure of `SimulationRequirementNode`
    objects based on various types of events and patterns in the AST.

    Attributes:
        requirement (Optional[SimulationRequirementNode]): Initialized to None.
            It is updated during the visit_hpl_pattern method based on the node's
            pattern type.

    """

    requirement: Optional[SimulationRequirementNode]

    def __init__(self) -> None:
        """
        Class constructor.
        Initializes internal data structures.
        """
        self.requirement = None

    def __initialize_disjunction_requirement_event(self, event: HplEventDisjunction) -> SimulationRequirementNode:
        """
        Parses an HplEventDisjunction object, extracting and linking its constituent
        simulation requirement nodes into a DisjointSimulationRequirementNode
        structure, representing a disjunction requirement event.

        """
        disjoint_node = DisjointSimulationRequirementNode()

        # Parse "event1"
        child1 = self.__extract_simulation_requirement_node(event.event1)
        disjoint_node.children.append(child1)
        child1.father = disjoint_node

        # Parse "event2"
        child2 = self.__extract_simulation_requirement_node(event.event2)
        disjoint_node.children.append(child2)
        child2.father = disjoint_node

        return disjoint_node

    def __initialize_simple_requirement_node(self, event: HplSimpleEvent) -> SimulationRequirementNode:
        """
        Initializes a SimpleSimulationRequirementNode with properties from an event
        and a callback function generated based on the predicate type (vacuous
        truth or binary operator).

        """
        generator = CallbackGenerator()
        if isinstance(event.predicate, HplVacuousTruth):
            callback = generator.process_vacuous_truth()
        else:
            callback = generator.process_binary_operator(event.predicate.condition)

        simple_node = SimpleSimulationRequirementNode(
            event.topic.value,
            event.msg_type.value,
            callback,
            predicate=str(event.predicate)
        )
        return simple_node

    def __extract_simulation_requirement_node(self, event: HplEvent) -> SimulationRequirementNode:
        """
        Extracts a simulation requirement node from an input event, returning it
        as a SimulationRequirementNode object. It handles three types of events:
        HplSimpleEvent, HplEventDisjunction, and raises an exception for unknown
        event subclasses.

        """
        if isinstance(event, HplSimpleEvent):
            return self.__initialize_simple_requirement_node(event)
        elif isinstance(event, HplEventDisjunction):
            return self.__initialize_disjunction_requirement_event(event)
        else:
            # TODO: proper error handler
            raise Exception(f'Unknown HplEvent subclass {type(event)}')

    def visit_hpl_pattern(self, node: HplPattern) -> None:
        """
        Visits an HPLPattern node and creates a corresponding simulation requirement
        node based on the pattern type, setting its timeout value. It also extracts
        child nodes and adds them to the created requirement node's children list.

        Args:
            node (HplPattern): Expected to be an instance of this class.

        """
        if node.is_existence:
            self.requirement = ExistenceSimulationRequirementNode(timeout=node.max_time)
        elif node.is_absence:
            self.requirement = AbsenceSimulationRequirementNode(timeout=node.max_time)
        elif node.is_response:
            self.requirement = ResponseSimulationRequirementNode(timeout=node.max_time)
        elif node.is_requirement:
            self.requirement = RequirementSimulationRequirementNode(timeout=node.max_time)
        elif node.is_prevention:
            self.requirement = PreventionSimulationRequirementNode(timeout=node.max_time)

        assert isinstance(self.requirement, SimulationRequirementNode)

        for child in node.children():
            child_node = self.__extract_simulation_requirement_node(child)
            child_node.father = self.requirement
            self.requirement.children.append(child_node)


class SimulationRequirementsParser:
    """
    Parses a string input representing simulation requirements and returns a
    structured representation of the requirements as an instance of `SimulationRequirementNode`.

    Attributes:
        __parser (property_parser): Used to parse HPL requirement strings into
            abstract syntax trees (ASTs).

    """

    def __init__(self) -> None:
        """
        Class constructor.
        """
        self.__parser = property_parser()

    def parse(self, hpl_requirement: str) -> SimulationRequirementNode:
        """
        Parses an HPL requirement string using a parser, traverses the resulting
        Abstract Syntax Tree (AST), and applies a visitor to each node to extract
        the simulation requirement into a SimulationRequirementNode object.

        Args:
            hpl_requirement (str): Expected to contain an HPL (High Performance
                Linpack) requirement. The exact format and structure of this string
                are not specified.

        Returns:
            SimulationRequirementNode: Initialized by a SimulationRequirementsVisitor
            after parsing an HPL requirement string and traversing its abstract
            syntax tree (AST).

        """
        visitor = SimulationRequirementsVisitor()

        ast = self.__parser.parse(hpl_requirement)

        for node in ast.iterate():
            node.accept(visitor)

        assert isinstance(visitor.requirement, SimulationRequirementNode)
        return visitor.requirement
