import copy
import signal
from rigel.exceptions import RigelError
from rigel.executor import (
    ConcurrentStagesExecutor,
    ParallelStageExecutor,
    SequentialStageExecutor,
    StageExecutor
)
from rigel.files.decoder import HEADER_GLOBAL_VARIABLE, YAMLDataDecoder
from rigel.files.loader import YAMLDataLoader
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginDataModel
from rigel.models.rigelfile import Rigelfile
from rigel.models.sequence import (
    ConcurrentStage,
    ParallelStage,
    Sequence,
    SequenceJobEntry,
    SequentialStage
)
from rigel.providers.manager import ProviderManager
from rigel.providers.provider import Provider
from typing import Any, Dict, List, Optional, Union

LOGGER = get_logger()


class Orchestrator:

    """
    Manages and executes workflows defined in a YAML file (Rigelfile). It parses
    the file, initializes providers, connects/disconnects them, handles signals
    for stopping execution, creates executors for different stage types, generates
    an execution plan, and runs jobs or sequences.

    Attributes:
        rigelfile (Rigelfile|None): Initialized in the constructor method `__init__`.
            It contains a parsed YAML file, which is built using the ModelBuilder.
        providers (List[Provider]): Initially empty. It stores instances of Provider
            objects loaded from YAML data, representing various providers for
            executing jobs.
        providers_data (Dict[str,Any]): Used to store data related to providers.
            It appears that it stores provider-specific information, possibly
            loaded from YAML files, and is accessible to various methods in the
            Orchestrator class.
        __provider_manager (ProviderManager): Initialized as ProviderManager().
            It seems to be responsible for managing providers, possibly loading
            or creating instances based on provider data from the Rigelfile.
        __job_shared_data (Dict[str,Any]): Used to share data between stages of a
            job. It is initially set to an empty dictionary when a new job starts
            executing and can be updated by each stage during its execution.
        __current_stage (Optional[StageExecutor]): Used to keep track of the current
            stage being executed. It is updated when a new stage is started with
            its corresponding job shared data.
        initializate_providers (NoneNone): Called during the initialization process
            of the Orchestrator object. It initializes providers from the Rigelfile
            by loading each provider based on its data in the Rigelfile and adding
            them to the list of providers.

    """
    def __init__(self, rigelfile: str) -> None:
        """
        Initializes and parses YAML rigelfile data, constructs variables and
        yaml_data from it, builds Rigelfile model using ModelBuilder, and sets up
        internal state including providers, provider manager, job shared data, and
        current stage executor.

        Args:
            rigelfile (str): Required to parse YAML Rigelfile.

        """

        # Parse YAML Rigelfile
        loader = YAMLDataLoader(rigelfile)
        raw_yaml_data = loader.load()

        # Decode global template variables
        decoder = YAMLDataDecoder()

        if raw_yaml_data.get('vars', None):

            variables = decoder.decode(
                raw_yaml_data.get('vars'),
                raw_yaml_data.get('vars'),
                HEADER_GLOBAL_VARIABLE
            )

        else:
            variables = {}

        yaml_data = decoder.decode(
            raw_yaml_data,
            variables,
            HEADER_GLOBAL_VARIABLE
        )

        # Initialize internal data structures
        self.rigelfile: Rigelfile = ModelBuilder(Rigelfile).build([], yaml_data)
        assert isinstance(self.rigelfile, Rigelfile)

        self.providers: List[Provider] = []
        self.providers_data: Dict[str, Any] = {}
        self.__provider_manager: ProviderManager = ProviderManager()
        self.__job_shared_data: Dict[str, Any] = {}

        self.__current_stage: Optional[StageExecutor] = None

        # Initialize providers
        self.initializate_providers()

    def initializate_providers(self) -> None:
        """
        Initializes providers by iterating over the items in `self.rigelfile.providers`,
        loads each provider using `__provider_manager.load`, and appends it to `self.providers`.

        """
        for provider_id, provider_data in self.rigelfile.providers.items():
            self.providers.append(
                self.__provider_manager.load(
                    provider_data.provider,
                    provider_id,
                    provider_data.with_,
                    self.rigelfile.vars,
                    self.providers_data
                )
            )

    def connect_providers(self) -> None:
        """
        Connects to multiple providers by iterating over a list of providers and
        calling their respective `connect` methods.

        """
        LOGGER.info("Connecting to providers")
        for provider in self.providers:
            provider.connect()

    def disconnect_providers(self) -> None:
        """
        Disconnects from all registered providers by calling their respective
        `disconnect` methods, logging an informational message before starting the
        disconnection process.

        """
        LOGGER.info("Disconnecting from providers")
        for provider in self.providers:
            provider.disconnect()

    def handle_signals(self) -> None:
        """
        Sets up handlers for SIGINT and SIGTSTP signals, allowing the program to
        respond to user attempts to terminate it (e.g., pressing CTRL-C or CTRL-Z).
        A warning message is also logged to inform users of this possibility.

        """
        signal.signal(signal.SIGINT, self.handle_abort)
        signal.signal(signal.SIGTSTP, self.handle_abort)
        LOGGER.warning("Press CTRL-C / CTRL-Z to stop execution")

    def handle_abort(self, *args: Any) -> None:
        """
        Terminates execution, logs an error message, and cancels any ongoing stage
        if present, then exits with a non-zero status code (1).

        Args:
            *args (Any): List of positional arguments

        """
        print()  # to avoid ^C character on the same line
        LOGGER.error('Stopping execution')
        if self.__current_stage:
            self.__current_stage.cancel()
            self.__current_stage = None
        # print(self.__job_shared_data)
        exit(1)

    def get_job_data(
        self,
        job: Union[str, SequenceJobEntry]
    ) -> PluginDataModel:

        """
        Retrieves and returns job data from the `rigelfile` object based on a given
        job identifier. If the job identifier is a string, it directly accesses
        the corresponding job data; otherwise, it updates the retrieved job data
        with additional information provided in the `job` parameter.

        Args:
            job (Union[str, SequenceJobEntry]): Required for this method to execute.
                It represents either a string job identifier or an object of class
                SequenceJobEntry with a name attribute.

        Returns:
            PluginDataModel: A deep copy of the specified job data from the
            rigelfile. The returned value includes any additional updates made to
            the job data by the SequenceJobEntry object if applicable.

        """
        try:

            if isinstance(job, str):
                job_identifier = job
                job_data = copy.deepcopy(self.rigelfile.jobs[job_identifier])

            else:  # isinstance(job, SequenceJobEntry)
                job_identifier = job.name
                job_data = copy.deepcopy(self.rigelfile.jobs[job_identifier])
                job_data.with_.update(job.with_)

            return job_data

        except KeyError:
            raise RigelError(f"Unknown job '{job_identifier}'")

    def create_sequential_executor(self, stage: SequentialStage) -> SequentialStageExecutor:
        """
        Creates a SequentialStageExecutor instance, which executes jobs sequentially.
        The executor is initialized with job data from the given SequentialStage,
        obtained through the get_job_data method.

        Args:
            stage (SequentialStage): Expected to be an instance of a class that
                represents a sequential processing stage, likely containing multiple
                jobs.

        Returns:
            SequentialStageExecutor: Initialized with a list of job data obtained
            from the jobs in the provided SequentialStage.

        """
        return SequentialStageExecutor(
            [self.get_job_data(job) for job in stage.jobs]
        )

    def create_concurrent_executor(self, stage: ConcurrentStage) -> ConcurrentStagesExecutor:
        """
        Creates and returns an instance of ConcurrentStagesExecutor, passing two
        lists as arguments: one for job data and another for dependency data from
        the provided ConcurrentStage object.

        Args:
            stage (ConcurrentStage): Expected to represent a concurrent processing
                stage that consists of jobs and their dependencies.

        Returns:
            ConcurrentStagesExecutor: Initialized with two lists: one containing
            the job data for each job in the given `stage`, and another containing
            the job data for each dependency of those jobs.

        """
        return ConcurrentStagesExecutor(
            [self.get_job_data(job) for job in stage.jobs],
            [self.get_job_data(job) for job in stage.dependencies],
        )

    def create_parallel_executor(self, stage: ParallelStage) -> ParallelStageExecutor:
        """
        Creates an executor for a parallel stage by recursively creating executors
        for its inner stages and combining them into a single ParallelStageExecutor
        instance.

        Args:
            stage (ParallelStage): Expected to be an object with a "parallel"
                attribute containing a list of inner stages, each of which can be
                either SequentialStage or ConcurrentStage.

        Returns:
            ParallelStageExecutor: Initialized with a list of inner stages and a
            matrix. The inner stages are created by recursively calling other
            functions based on their types, i.e., SequentialStage or ConcurrentStage.

        """
        inner_stages = []
        for inner_stage in stage.parallel:
            if isinstance(inner_stage, SequentialStage):
                inner_stages.append(self.create_sequential_executor(inner_stage))
            elif isinstance(inner_stage, ConcurrentStage):
                inner_stages.append(self.create_concurrent_executor(inner_stage))
        print()

        return ParallelStageExecutor(inner_stages, stage.matrix)

    def generate_execution_plan(self, sequence: Sequence) -> List[StageExecutor]:
        """
        Generates an execution plan by iterating over a sequence of stages and
        creating corresponding stage executors based on their types (Parallel,
        Sequential, or Concurrent). The function returns a list of these stage executors.

        Args:
            sequence (Sequence): Assumed to be an object that contains stages,
                such as ParallelStage, SequentialStage, or ConcurrentStage. The
                exact nature of this sequence is not specified.

        Returns:
            List[StageExecutor]: A list of StageExecutor objects, each representing
            an executor for a stage in the input sequence. The order of the executors
            corresponds to the order of stages in the input sequence.

        """
        execution_plan: List[StageExecutor] = []
        for stage in sequence.stages:

            if isinstance(stage, ParallelStage):
                executor = self.create_parallel_executor(stage)
            elif isinstance(stage, SequentialStage):
                executor = self.create_sequential_executor(stage)
            elif isinstance(stage, ConcurrentStage):
                executor = self.create_concurrent_executor(stage)

            execution_plan.append(executor)

        return execution_plan

    def execute(self, execution_plan: List[StageExecutor]) -> None:
        """
        Executes a list of execution plans defined in the `execution_plan` parameter,
        iterating through each plan and executing its stages by calling their
        `execute` methods.

        Args:
            execution_plan (List[StageExecutor]): Expected to contain one or more
                StageExecutor instances, which represent the stages that need to
                be executed as part of the execution plan.

        """
        for stage in execution_plan:
            self.__current_stage = stage
            stage.job_shared_data = self.__job_shared_data

            stage.execute(
                self.rigelfile.vars,
                self.rigelfile.application,
                self.providers_data
            )

        self.__current_stage = None

    def run_job(self, job: str) -> None:
        """
        Executes a single job by creating an execution plan, handling signals,
        connecting providers, executing the plan, and disconnecting providers. It
        orchestrates the process of running a specific task or workflow.

        Args:
            job (str): Expected to be a single job being executed by this method.
                It specifies the job for which an execution plan is generated and
                then executed.

        """
        # Create a wrapper sequence for the single job being executed
        sequence = Sequence(
            stages=[SequentialStage(jobs=[job])]
        )

        execution_plan = self.generate_execution_plan(sequence)

        self.handle_signals()
        self.connect_providers()
        self.execute(execution_plan)
        self.disconnect_providers()

    def run_sequence(self, name: str) -> None:
        """
        Executes a specified sequence from a rigelfile, handling signals, connecting
        providers, and executing the plan. If the sequence is not found, it raises
        an error. The sequence is generated using the `generate_execution_plan` method.

        Args:
            name (str): Required for identifying a sequence from the rigelfile's
                sequences dictionary.

        """
        sequence = self.rigelfile.sequences.get(name, None)
        if not sequence:
            raise RigelError(f"Sequence '{name}' not found")

        execution_plan = self.generate_execution_plan(sequence)

        self.handle_signals()
        self.connect_providers()
        self.execute(execution_plan)
        self.disconnect_providers()
