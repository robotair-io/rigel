import boto3
import time
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers.aws import AWSProviderOutputModel
from rigel.plugins.plugin import Plugin as PluginBase
from typing import Any, Dict, List, Optional
from .models import PluginModel, DataSource

LOGGER = get_logger()


class Plugin(PluginBase):

    """
    Handles RoboMaker simulation job creation, management and interaction. It sets
    up a robot and simulation application if necessary, creates a simulation job,
    waits for its status to reach 'Running', and then stops it after the specified
    duration.

    Attributes:
        model (PluginModel): Created through ModelBuilder by calling `build([],
            self.raw_data)`. It represents a plugin model that contains details
            about robot applications, simulation applications, IAM roles, output
            locations, vpc configurations, and other related settings.
        raw_data (PluginRawData): Passed to the plugin during initialization. Its
            contents are not explicitly defined but are expected to contain the
            raw data required for the plugin's operation.

    """
    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:
        """
        Initializes an instance of the plugin by calling its superclass's constructor
        and then building a model for the plugin based on raw data. It asserts
        that the built model is an instance of the PluginModel class.

        Args:
            raw_data (PluginRawData): Passed to the superclass's initializer as
                well as used when building the model instance via ModelBuilder.
            global_data (RigelfileGlobalData): Passed to the class constructor.
                Its presence indicates that it is an input required for the
                initialization process.
            application (Application): Passed to the parent class's constructor
                along with other parameters.
            providers_data (Dict[str, Any]): Optional (with default value `{}`).
                It appears to hold data related to providers, possibly being used
                in the construction of the PluginModel.
            shared_data (Dict[str, Any]): Optional by default. It provides additional
                data that can be shared among different parts of the system. If
                not provided, it defaults to an empty dictionary.

        """
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

    def retrieve_robomaker_client(self) -> boto3.session.Session.client:

        """
        Retrieves and returns an AWS RoboMaker client based on a list of available
        AWS providers, ensuring only one provider is used and it is properly
        configured for RoboMaker operations.

        Returns:
            boto3.session.Session.client: A client object that can be used for
            interacting with Amazon RoboMaker service through Boto3, an SDK for AWS.

        """
        providers = [provider for _, provider in self.providers_data.items() if isinstance(provider, AWSProviderOutputModel)]

        if not providers:
            raise RigelError(base='No AWS provider were found. This plugin requires a connection to AWS RoboMaker.')
        elif len(providers) > 1:
            raise RigelError(base='Multiple AWS providers was found. Please specify which provider you want to use.')
        else:
            client = providers[0].robomaker_client
            if not client:
                raise RigelError(base='Selected AWS provider is not configured to work with AWS RoboMaker.')
            return client

    def create_robot_application(self) -> Dict[str, Any]:
        """
        Creates a new robot application using information from the model and logs
        the creation process. The method takes no arguments besides the self
        parameter, indicating it is part of a class.

        Returns:
            Dict[str, Any]: A new robot application object after it has been
            successfully created using the provided parameters.

        """
        kwargs = {
            'name': self.model.robot_application.name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'environment': {
                'uri': self.model.robot_application.ecr
            }
        }
        robot_application = self.__robomaker_client.create_robot_application(**kwargs)
        LOGGER.info(f"New robot application '{self.model.robot_application.name}' created with success")
        return robot_application

    def delete_robot_application(
        self,
        arn: str
    ) -> None:
        """
        Deletes a robot application specified by its Amazon Resource Name (ARN)
        using the RoboMaker client. The deletion is confirmed with an informational
        log message if successful.

        Args:
            arn (str): Required. It represents the Amazon Resource Name (ARN) for
                the robot application to be deleted.

        """
        kwargs = {'application': arn}
        self.__robomaker_client.delete_robot_application(**kwargs)
        LOGGER.info("Robot application deleted with success")

    def create_simulation_application(self) -> Dict[str, Any]:
        """
        Creates a new simulation application using the RoboMaker client, with
        parameters such as name, robot software suite, simulation software suite,
        and environment URI. It then logs an information message upon successful
        creation.

        Returns:
            Dict[str, Any]: An instance of a simulation application created by the
            AWS RoboMaker client using the provided parameters. The returned object
            is logged as a successful creation and then passed back to the caller.

        """
        kwargs = {
            'name': self.model.simulation_application.name,
            'robotSoftwareSuite': {
                'name': 'General'
            },
            'simulationSoftwareSuite': {
                'name': 'SimulationRuntime'
            },
            'environment': {
                'uri': self.model.simulation_application.ecr
            }
        }
        simulation_application = self.__robomaker_client.create_simulation_application(**kwargs)
        LOGGER.info(f"New simulation application '{self.model.simulation_application.name}' created with success")
        return simulation_application

    def delete_simulation_application(
        self,
        arn: str
    ) -> None:
        """
        Deletes a simulation application identified by its Amazon Resource Name
        (ARN). It uses the Robomaker client to send a DELETE request and logs a
        success message when the operation is complete.

        Args:
            arn (str): Required, representing an Amazon Resource Name (ARN) that
                uniquely identifies the simulation application to be deleted.

        """
        kwargs = {'application': arn}
        self.__robomaker_client.delete_simulation_application(**kwargs)
        LOGGER.info("Simulation application deleted with success")

    def convert_envs(self, envs: List[str]) -> Dict[str, str]:
        """
        Takes a list of environment variable strings and returns a dictionary where
        each key-value pair is extracted from the input string using the '='
        character as separator, with leading/trailing whitespaces removed.

        Args:
            envs (List[str]): Expected to contain strings representing environment
                variables, where each string is in the format 'key=value'.

        Returns:
            Dict[str, str]: A dictionary mapping environment variable names to
            their corresponding values. The input list of strings representing
            environment variables in 'key=value' format is converted into this dictionary.

        """
        result = {}
        for env in envs:
            key, value = env.split('=')
            result[key.strip()] = value.strip()
        return result

    def create_simulation_job(self) -> Dict[str, Any]:
        """
        Creates a RoboMaker simulation job based on the provided configuration
        data from the model and other dependent objects, and returns the created
        job. It also logs the creation event if successful.

        Returns:
            Dict[str, Any]: A dictionary representing the created simulation job.
            This includes information such as IAM role, output location, maximum
            job duration, VPC configuration, robot and simulation applications,
            compute configuration, data sources, and worldforge exported jobs.

        """
        kwargs = {
            'iamRole': self.model.iam_role,
            'outputLocation': {'s3Bucket': self.model.output_location} if self.model.output_location else {},
            'maxJobDurationInSeconds': self.model.simulation_duration,
            'vpcConfig': {
                'subnets': self.model.vpc_config.subnets,
                'securityGroups': self.model.vpc_config.securityGroups,
                'assignPublicIp': self.model.vpc_config.assignPublicIp
            },
        }

        if self.__robot_application is not None:

            kwargs['robotApplications'] = [
                {
                    'application': self.__robot_application['arn'],
                    'launchConfig': {
                        'streamUI': self.model.robot_application.streamUI,
                        'command': self.model.robot_application.command,
                        'environmentVariables': self.convert_envs(self.model.robot_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in self.model.robot_application.ports
                            ]
                        },
                    },
                    'tools': [tool.dict() for tool in self.model.robot_application.tools]
                }
            ]

        if self.__simulation_application is not None:

            kwargs['simulationApplications'] = [
                {
                    'application': self.__simulation_application['arn'],
                    'launchConfig': {
                        'streamUI': self.model.simulation_application.streamUI,
                        'command': self.model.simulation_application.command,
                        'environmentVariables': self.convert_envs(self.model.simulation_application.environment),
                        'portForwardingConfig': {
                            'portMappings': [
                                {
                                    'jobPort': ports[0],
                                    'applicationPort': ports[1],
                                    'enableOnPublicIp': True
                                }
                                for ports in self.model.simulation_application.ports
                            ]
                        },
                    },
                    'worldConfigs': [config.dict() for config in self.model.simulation_application.worldConfigs],
                    'tools': [tool.dict() for tool in self.model.simulation_application.tools]
                }
            ]

        # Add compute information
        if self.model.compute is not None:
            kwargs['compute'] = self.model.compute.dict()

        # Prepare data sources and WorldForge exports
        data_sources = [source.dict() for source in self.model.data_sources]
        if data_sources:
            kwargs['dataSources'] = data_sources

        # Check if a custom WorldForge export job was provided in the Rigelfile.
        worldforge_exported_jobs = [
            source for source in self.model.data_sources if source.s3Keys[0].startswith('aws-robomaker-worldforge-export')
        ]

        if not worldforge_exported_jobs:

            if self.model.worldforge_exported_job:

                kwargs['dataSources'].append(
                    DataSource(
                        name='ExportedWorldJob',
                        type='Archive',
                        **self.model.worldforge_exported_job
                    ).dict()
                )

        simulation_job = self.__robomaker_client.create_simulation_job(**kwargs)
        LOGGER.info('Created simulation job')
        return simulation_job

    def cancel_simulation_job(self, arn: str) -> None:
        """
        Cancels a specified simulation job using AWS RoboMaker's cancel_simulation_job
        API and logs the success to the LOGGER.

        Args:
            arn (str): Required to specify the Amazon Resource Name (ARN) of the
                simulation job that should be cancelled.

        """
        kwargs = {'job': arn}
        self.__robomaker_client.cancel_simulation_job(**kwargs)
        LOGGER.info('Simulation job canceled with success')

    def wait_simulation_job_status(self, status: str) -> None:
        """
        Waits for a simulation job to reach a specific status (e.g., 'SUCCEEDED',
        'FAILED') by periodically querying the AWS RoboMaker client and updating
        the local simulation job data until the desired status is reached.

        Args:
            status (str): Used to specify the expected status of the simulation
                job. It determines when the waiting loop should terminate, as the
                function checks if the simulation job's status matches this specified
                value.

        """
        kwargs = {'job': self.__simulation_job['arn']}
        LOGGER.info(f"Waiting for simulation job status to be '{status}'")
        while True:
            simulation_job_data = self.__robomaker_client.describe_simulation_job(**kwargs)
            if simulation_job_data['status'] == status:
                self.__simulation_job = simulation_job_data
                break
            time.sleep(0.5)

    def get_robot_application(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves a robot application from Robomaker based on its name, returns
        the found application if exists and logs an info message, otherwise returns
        None.

        Returns:
            Optional[Dict[str, Any]]: Either a dictionary representing an existing
            robot application summary or None if no such application is found.

        """
        kwargs = {
            "maxResults": 1,
            "filters":
            [
                {
                    "name": "name",
                    "values": [self.model.robot_application.name]
                }
            ]
        }
        response = self.__robomaker_client.list_robot_applications(**kwargs)
        if response['robotApplicationSummaries']:
            LOGGER.info(f"Found existing robot application '{self.model.robot_application.name}'")
            return response['robotApplicationSummaries'][0]
        return None

    def get_simulation_application(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves a simulation application from Robomaker using the provided client.
        If the application exists, it returns the summary of the first result;
        otherwise, it returns None.

        Returns:
            Optional[Dict[str, Any]]: Either a dictionary representing a simulation
            application summary or None if no matching simulation application is
            found.

        """
        kwargs = {
            "maxResults": 1,
            "filters":
            [
                {
                    "name": "name",
                    "values": [self.model.simulation_application.name]
                }
            ]
        }
        response = self.__robomaker_client.list_simulation_applications(**kwargs)
        if response['simulationApplicationSummaries']:
            LOGGER.info(f"Found existing simulation application '{self.model.simulation_application.name}'")
            return response['simulationApplicationSummaries'][0]
        return None

    def setup(self) -> None:
        """
        Initializes and configures various components for RoboMaker simulations,
        including retrieving clients, obtaining or creating robot and simulation
        applications, and creating a simulation job based on provided model settings.

        """
        self.__robomaker_client = self.retrieve_robomaker_client()

        self.__robot_application = None
        self.__simulation_application = None

        if self.model.robot_application is not None:
            self.__robot_application = self.get_robot_application() or self.create_robot_application()

        if self.model.simulation_application is not None:
            self.__simulation_application = self.get_simulation_application() or self.create_simulation_application()

        self.__simulation_job = self.create_simulation_job()

    def start(self) -> None:

        """
        Initializes simulation job status and retrieves simulation duration, public
        IP address, and port. It then populates shared data with these values and
        prints the accessible URL for the simulation job.

        """
        self.wait_simulation_job_status('Running')

        simulation_job_duration = self.model.simulation_duration
        self.shared_data["simulation_duration"] = simulation_job_duration

        if self.__robot_application is not None:

            simulation_job_public_ip = self.__simulation_job['networkInterface']['publicIpAddress']
            self.shared_data["simulation_address"] = simulation_job_public_ip

            simulation_job_public_port = self.model.robot_application.ports[0][0]
            self.shared_data["simulation_port"] = simulation_job_public_port

            print(f'Simulation job can be accessed on {simulation_job_public_ip}:{simulation_job_public_port}')

    def process(self) -> None:

        """
        Waits for a simulation job to finish, displaying informative messages
        during that time. If no cancellation signal (CTRL-C/CTRL-Z) is received
        within the specified duration, it pauses execution for the same duration
        using `time.sleep`.

        """
        if self.model.simulation_duration:

            LOGGER.info("Waiting for simulation job to finish.")
            LOGGER.info("Press CTRL-C/CTRL-Z to cancel simulation job.")

            time.sleep(self.model.simulation_duration)

    def stop(self) -> None:
        """
        Cancels a simulation job, deletes a robot application, and deletes a
        simulation application if they exist, indicating a shutdown or termination
        process for these entities.

        """
        self.cancel_simulation_job(self.__simulation_job['arn'])

        if self.__robot_application is not None:
            self.delete_robot_application(self.__robot_application['arn'])

        if self.__simulation_application is not None:
            self.delete_simulation_application(self.__simulation_application['arn'])
