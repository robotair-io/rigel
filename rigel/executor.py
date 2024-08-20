import copy
import itertools
import threading
from rigel.files.decoder import HEADER_SHARED_DATA, YAMLDataDecoder
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.plugin import PluginDataModel
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.models.sequence import (
    ConcurrentStage,
    SequentialStage
)
from rigel.plugins.manager import PluginManager
from rigel.plugins.plugin import Plugin
from typing import Any, Dict, List, Optional, Union


LOGGER = get_logger()


class StageExecutor:

    """
    Defines a blueprint for an executor that manages the execution of stages in a
    pipeline. It provides methods for cancelling and executing stages, with the
    latter requiring global data, application information, and provider data as inputs.

    Attributes:
        job_shared_data (Dict[str, Any]): Initialized with default values. It can
            be accessed as a shared data structure among all job executions within
            this executor.

    """
    job_shared_data: Dict[str, Any] = {}

    def cancel(self) -> None:
        raise NotImplementedError

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:
        """
        Takes three parameters and raises a NotImplementedError. Its purpose is
        to execute a stage, but it does not provide any concrete implementation,
        making it abstract or placeholder for actual execution functionality that
        may be implemented later.

        Args:
            global_data (RigelfileGlobalData): Expected to be passed when the
                function is called. It represents global data related to Rigel,
                which is likely a software or system component.
            application (Application): Expected to be an instance of a class
                representing an application.
            providers_data (Dict[str, Any]): Expected to be a dictionary where
                keys are strings and values can be any Python object (Any). The
                purpose of this parameter is not explicitly stated.

        """
        raise NotImplementedError


class LoaderStageExecutor(StageExecutor):

    """
    Loads a plugin using data from a `job`, `global_data`, and other parameters.
    It decodes raw data into a decoded raw data format, then uses a plugin manager
    to load the plugin with the processed data.

    Attributes:
        __plugin_manager (PluginManager): Initialized with a default value. It
            manages plugins for the loader stage executor.

    """
    __plugin_manager: PluginManager = PluginManager()

    def load_plugin(
        self,
        job: PluginDataModel,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any],
        overwrite_data: Dict[str, Any] = {}  # noqa
    ) -> Plugin:
        """
        Loads and initializes a plugin, given job data, global data, application
        data, provider data, shared data, and optional overwrite data. It decodes
        the job data using YAML and then uses the decoded data to load the plugin.

        Args:
            job (PluginDataModel): Required. It contains data that needs to be
                loaded for a plugin.
            global_data (RigelfileGlobalData): Not defined within this code snippet.
                Its purpose would depend on its definition and usage elsewhere in
                the code.
            application (Application): Passed to the function when it is called.
            providers_data (Dict[str, Any]): Expected to be a dictionary containing
                data related to providers. The exact structure and content of this
                dictionary are not specified in the provided code snippet.
            shared_data (Dict[str, Any]): Passed to the `decode` method of the
                YAMLDataDecoder class. It contains shared data used during decoding
                of job raw data.
            overwrite_data (Dict[str, Any]): Optional with default value of an
                empty dictionary. It allows for overwriting data from the job's
                raw data with new data provided by this parameter.

        Returns:
            Plugin: Loaded by calling the method `self.__plugin_manager.load()`
            with the provided parameters.

        """

        job_raw_data = job.with_

        if overwrite_data:
            job_raw_data.update(overwrite_data)

        decoder = YAMLDataDecoder()
        job_decoded_raw_data = decoder.decode(
            job_raw_data,
            shared_data,
            HEADER_SHARED_DATA
        )

        return self.__plugin_manager.load(
            job.plugin,
            job_decoded_raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )


class ExecutionBranch(threading.Thread):

    """
    Executes a list of stages asynchronously, managing job shared data and interacting
    with global application data and providers. Each stage is executed by setting
    its job shared data and executing it with provided data. The current stage can
    be cancelled if needed.

    Attributes:
        stages (List[Union[SequentialStage,ConcurrentStage]]): Initialized during
            the __init__ method with a list of stages which can be either
            SequentialStage or ConcurrentStage.
        job_shared_data (Dict[str,Any]): Initialized with a dictionary that contains
            data shared among all stages within a job during execution. This data
            is set from outside the class.
        __current_stage (Optional[Union[SequentialStage,ConcurrentStage]]): Used
            to keep track of the current stage being executed within the execution
            branch. It is initialized as None and updated in each iteration of the
            loop in the run method.
        __global_data (RigelfileGlobalData): Initialized during the `__init__`
            method. It represents global data for a rigelfile application.
        __application (Application): Referenced by the `run` method. It appears
            to be a representation of an application related to job execution,
            possibly holding configuration or control data used during the execution
            process.
        __providers_data (Dict[str,Any]): Passed to the constructor. It likely
            holds data related to service providers or resources utilized by the
            stages during execution.

    """
    def __init__(
        self,
        stages: List[Union[SequentialStage, ConcurrentStage]],
        job_shared_data: Dict[str, Any],
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:
        """
        Initializes an instance of the class, setting attributes for stages, shared
        data, global data, application, and providers data. It also initializes a
        current stage attribute to None.

        Args:
            stages (List[Union[SequentialStage, ConcurrentStage]]): Expected to
                hold one or more instances of either SequentialStage or ConcurrentStage.
            job_shared_data (Dict[str, Any]): Assigned to an instance variable
                with the same name. It appears to hold data shared among stages
                of an execution branch related to a job.
            global_data (RigelfileGlobalData): Assigned to the instance variable
                `self.__global_data`.
            application (Application): Stored in the instance variable
                `self.__application`. It represents an instance of the application
                class, which likely contains information about the application's
                configuration or state.
            providers_data (Dict[str, Any]): Expected to be a dictionary containing
                data related to providers, which are not further specified. It
                will be stored as an instance variable in the `ExecutionBranch` class.

        """
        super(ExecutionBranch, self).__init__()

        self.stages = stages
        self.job_shared_data = job_shared_data

        self.__current_stage: Optional[Union[SequentialStage, ConcurrentStage]] = None

        self.__global_data = global_data
        self.__application = application
        self.__providers_data = providers_data

    def cancel(self) -> None:
        """
        Cancels its current stage if it exists, and then resets the stage to None,
        effectively terminating any ongoing operation.

        """
        if self.__current_stage:
            self.__current_stage.cancel()
            self.__current_stage = None

    def run(self) -> None:

        """
        Iterates through each stage in the stages list, assigns current stage and
        shared job data to it, then executes the stage with provided global data,
        application, and providers data.

        """
        for stage in self.stages:
            self.__current_stage = stage
            stage.job_shared_data = self.job_shared_data
            stage.execute(
                self.__global_data,
                self.__application,
                self.__providers_data
            )

        self.__current_stage = None


class ParallelStageExecutor(StageExecutor):

    """
    Executes multiple combinations of stages and shared data in parallel, utilizing
    threads for concurrency. It takes in a list of stages, a matrix of data, and
    various global and application-specific parameters to create and execute
    execution branches.

    Attributes:
        stages (List[Union[SequentialStage,ConcurrentStage]]): Initialized during
            the `__init__` method. It contains a list of stages that can be either
            sequential or concurrent.
        matrix (Dict[str,List[Any]]): Initialized during the `__init__` method.
            It represents a matrix-like data structure where keys are strings and
            values are lists, possibly containing Any type objects.
        threads (List[ExecutionBranch]): Populated by instances of the ExecutionBranch
            class, each representing a separate thread for executing a stage
            executor's execution branch.

    """
    def __init__(self, stages: List[Union[SequentialStage, ConcurrentStage]], matrix: Dict[str, List[Any]]) -> None:
        """
        Initializes three attributes: stages, matrix, and threads. The `stages`
        attribute holds a list of either Sequential or Concurrent stage objects,
        while `matrix` is a dictionary mapping strings to lists of arbitrary types.
        The `threads` attribute is initialized as an empty list.

        Args:
            stages (List[Union[SequentialStage, ConcurrentStage]]): Initialized
                with a list of stages that can be either SequentialStage or
                ConcurrentStage objects.
            matrix (Dict[str, List[Any]]): Initialized with an empty dictionary.
                This parameter maps string keys to lists of any data type (`Any`).

        """
        self.stages = stages
        self.matrix = matrix
        self.threads = []

    def __combine_matrix_data(self, matrix: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generates all possible combinations of values from the input matrix, where
        each key corresponds to a list of values. It then constructs dictionaries
        for these combinations and returns them as a list.

        """
        keys = matrix.keys()
        values = matrix.values()

        # NOTE: it returns [{}] if no matrix data was provided.
        # This ensures that 'execute' can always be called.

        combinations = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    def __decode_matrix_data(self) -> Dict[str, List[Any]]:

        """
        Decodes YAML data from a matrix using a YAMLDataDecoder instance, taking
        into account job-shared data and header shared data.

        """
        decoder = YAMLDataDecoder()
        return decoder.decode(
            self.matrix,
            self.job_shared_data,
            HEADER_SHARED_DATA
        )

    def cancel(self) -> None:
        """
        Cancels all threads associated with it by calling their respective `cancel`
        methods, effectively terminating any ongoing tasks or operations within
        those threads.

        """
        for thread in self.threads:
            thread.cancel()

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any]
    ) -> None:

        """
        Executes multiple threads concurrently, utilizing a combination of data
        from global_data and providers_data to create local execution stages. It
        initializes and runs these threads, then waits for their completion.

        Args:
            global_data (RigelfileGlobalData): Passed as an argument when calling
                this method. It provides global data related to the Rigelfile
                application, likely including configuration settings, constants,
                or other shared information.
            application (Application): Passed as an argument to the function when
                it is called.
            providers_data (Dict[str, Any]): Expected to be a dictionary where
                keys are string values and values can be of any type.

        """
        decoded_matrix = self.__decode_matrix_data()
        combinations = self.__combine_matrix_data(decoded_matrix)

        for combination in combinations:

            # NOTE: a deep copy of data is passed to each thread
            # to avoid conflicts
            local_shared_data = copy.deepcopy(self.job_shared_data)
            local_shared_data.update(combination)

            local_stages = copy.deepcopy(self.stages)

            self.threads.append(
                ExecutionBranch(
                    local_stages,
                    local_shared_data,
                    global_data,
                    application,
                    providers_data
                )
            )

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()

        # TODO: consider / implement a mechanism that allows shared plugin data to passed
        # from a ParallelStageExecutor instance to other stage executors


class SequentialStageExecutor(LoaderStageExecutor):

    """
    Executes a list of jobs sequentially, loading each job from a model, setting
    it up, starting it, processing it, and stopping it, before moving on to the
    next job. It also allows for cancellation of the current job if needed.

    Attributes:
        job_models (List[PluginDataModel]): Initialized with a list of jobs during
            object creation. It represents the collection of job models to be
            executed by the executor.
        __current_job (Optional[Plugin]): Initialized to `None`. It keeps track
            of the current job being executed, updated after each iteration in the
            execution loop.

    """
    def __init__(self, jobs: List[PluginDataModel]) -> None:
        """
        Initializes an instance, taking a list of PluginDataModel objects as input,
        and assigns it to self.job_models. It also initializes self.current_job
        as None, indicating no current job is set.

        Args:
            jobs (List[PluginDataModel]): Assigned to an instance variable
                `self.job_models`. It accepts a collection of PluginDataModel
                objects, which are presumably used to initialize or configure the
                class.

        """
        self.job_models = jobs
        self.__current_job: Optional[Plugin] = None

    def cancel(self) -> None:
        """
        Cancels any ongoing job if one exists, by calling its `stop` method and
        then resetting `self.__current_job` to None, effectively releasing resources
        associated with the job.

        """
        if self.__current_job:
            self.__current_job.stop()
            self.__current_job = None

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:

        """
        Iterates over job models, loads each job plugin, sets it up, starts it,
        processes its tasks, and stops it before moving to the next one. It also
        keeps track of the current job being executed.

        Args:
            global_data (RigelfileGlobalData): Passed to the method.
            application (Application): Not further defined or described within
                this snippet. Its purpose is to be used as an argument for the
                `load_plugin` method.
            providers_data (Dict[str, Any]): Expected to contain data related to
                providers. It can be any valid dictionary that maps strings to
                objects of varying types.

        """
        for job_model in self.job_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            assert isinstance(job, Plugin)

            self.__current_job = job

            job.setup()
            job.start()
            job.process()
            job.stop()

        self.__current_job = None


class ConcurrentStagesExecutor(LoaderStageExecutor):

    """
    Executes a list of jobs and their dependencies concurrently, allowing for
    parallel processing. It loads plugins, sets up, starts, processes, and stops
    each job, managing dependencies and canceling jobs as needed.

    Attributes:
        job_models (List[PluginDataModel]): Populated with a list of PluginDataModel
            objects during initialization of the class instance.
        dependency_models (List[PluginDataModel]): Used to store a list of
            PluginDataModel objects, representing the dependencies for the job
            execution process.
        __current_job (Optional[Plugin]): Initialized to None. It holds the reference
            to the currently executing job plugin, which changes during the execution
            process.
        __dependencies (List[Plugin]): Used to store instances of Plugin that are
            loaded from dependency_models. It stores the dependencies for processing
            after all jobs have been executed.

    """
    def __init__(self, jobs: List[PluginDataModel], dependencies: List[PluginDataModel]) -> None:
        """
        Initializes its instance variables, storing lists of job and dependency
        models, and setting up two additional variables to track the current job
        and dependencies as Plugin objects.

        Args:
            jobs (List[PluginDataModel]): Assigned to the instance variable `self.job_models`.
            dependencies (List[PluginDataModel]): Populated with PluginDataModel
                objects representing dependencies between jobs.

        """
        self.job_models = jobs
        self.dependency_models = dependencies

        self.__current_job: Optional[Plugin] = None
        self.__dependencies: List[Plugin] = []

    def cancel(self) -> None:

        """
        Cancels any active jobs and dependencies, stopping their execution by
        calling their respective stop methods. It ensures that all ongoing tasks
        are terminated when cancellation is requested.

        """
        if self.__current_job:
            self.__current_job.stop()
            self.__current_job = None

        for job in self.__dependencies:
            job.stop()

    def execute(
        self,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
    ) -> None:

        """
        Initializes and runs multiple jobs based on provided data, dependencies,
        and application settings. It sets up, starts, processes, and stops each
        job before finally stopping all dependent jobs.

        Args:
            global_data (RigelfileGlobalData): Passed to the `load_plugin` method
                for each dependency model or job model. It seems to be an object
                containing global data that can be used by plugins.
            application (Application): Passed to the method from outside its scope,
                possibly representing an instance of some application framework
                or class that provides context for job execution.
            providers_data (Dict[str, Any]): Expected to be a dictionary that maps
                strings (keys) to objects of type Any (values).

        """
        for job_model in self.dependency_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            self.__dependencies.append(job)
            assert isinstance(job, Plugin)

            job.setup()
            job.start()

        for job_model in self.job_models:

            job = self.load_plugin(
                job_model,
                global_data,
                application,
                providers_data,
                self.job_shared_data
            )
            assert isinstance(job, Plugin)

            self.__current_job = job

            job.setup()
            job.start()
            job.process()
            job.stop()

        self.__current_job = None

        for job in self.__dependencies:
            job.stop()
