import boto3
from copy import deepcopy
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from rigel.providers.aws import AWSProviderOutputModel
from time import sleep
from typing import Any, Dict, List
from .models import PluginModel


LOGGER = get_logger()


class Plugin(PluginBase):

    """
    Initializes a RoboMaker plugin, retrieves an AWS provider, generates worlds,
    exports them to S3, and stores the export job details for further processing.
    It uses various RoboMaker APIs to interact with AWS services.

    Attributes:
        model (PluginModel): Built using ModelBuilder. It represents a model for
            RoboMaker world generation and is used to specify parameters such as
            template ARN, floor plan count, and interior count.
        raw_data (PluginRawData): Passed to the constructor. Its purpose and
            contents are not explicitly mentioned, but it likely contains input
            data for the plugin to process.
        __robomaker_client (boto3sessionSessionclient|None): Initialized through
            the `__retrieve_robomaker_client` method, which retrieves the RoboMaker
            client from an AWS provider. It returns None if the selected AWS
            provider is not configured to work with RoboMaker.
        __retrieve_robomaker_client (boto3sessionSessionclient|None): Responsible
            for retrieving a RoboMaker client from the providers data, ensuring
            that only one AWS provider exists.

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
        Initializes an instance of the Plugin with the provided parameters, including
        raw data, global data, application, providers data and shared data. It
        also builds a model from the raw data and retrieves a Robomaker client.

        Args:
            raw_data (PluginRawData): Expected to be an instance of the PluginRawData
                class, providing raw data required for initializing this class.
            global_data (RigelfileGlobalData): Used to initialize an instance of
                the class.
            application (Application): Passed to the class initializer along with
                other parameters. It is used as an argument in the super().__init__
                call, but its specific purpose or usage within the class is not
                directly apparent.
            providers_data (Dict[str, Any]): Required to initialize an instance
                of this class. It represents data provided by plugins.
            shared_data (Dict[str, Any]): Optional by default with an empty
                dictionary `{}` as its value. It can be overridden when creating
                an instance of this class.

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

        self.__robomaker_client = self.__retrieve_robomaker_client()

    def __retrieve_robomaker_client(self) -> boto3.session.Session.client:

        """
        Retrieves an AWS RoboMaker client from a list of available AWS providers.
        If no provider is found, it raises an error. It returns the client if only
        one provider is available and configured correctly for RoboMaker use.

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

    def __generate_worlds(self) -> str:

        """
        Generates RoboMaker worlds based on a specified template, floor plan count,
        and interior count per floor plan. It creates a world generation job, waits
        for its completion, and returns the job's ARN.

        """
        response = self.__robomaker_client.create_world_generation_job(
            template=self.model.template_arn,
            worldCount={
                'floorplanCount': self.model.floor_plan_count,
                'interiorCountPerFloorplan': self.model.interior_count
            }
        )

        LOGGER.info("Running world generation job")
        generation_job_arn = response["arn"]
        while self.__robomaker_client.describe_world_generation_job(job=generation_job_arn)["status"] != "Completed":
            sleep(0.5)

        LOGGER.info("Finished world generation job")
        return generation_job_arn

    def __get_worlds_information(self, generation_job_arn: str) -> List[str]:

        """
        Retrieves a list of ARNs for worlds associated with a specific generation
        job, using the RoboMaker client's `list_worlds` method and filtering results
        based on the provided job ARN.

        """
        worlds = self.__robomaker_client.list_worlds()
        world_list = []

        for world in worlds["worldSummaries"]:
            if world["generationJob"] == generation_job_arn:
                world_list.append(world["arn"])

        return world_list

    def __export_worlds(self, worlds: List[str], s3prefix: str) -> List[str]:

        """
        Exports multiple worlds to an S3 bucket, creating a world export job for
        each world and monitoring the status of the jobs until they are completed.

        """
        export_job_arns = []

        for world in worlds:
            response = self.__robomaker_client.create_world_export_job(
                worlds=[world],
                outputLocation={
                    's3Bucket': self.model.s3_bucket,
                    's3Prefix': s3prefix
                },
                iamRole=self.model.iam_role
            )

            export_job_arns.append(response["arn"])

        temp_arns = deepcopy(export_job_arns)

        LOGGER.info("Running export job")
        while temp_arns:
            for arn in temp_arns:
                if self.__robomaker_client.describe_world_export_job(job=arn)["status"] == "Completed":
                    temp_arns.remove(arn)
            sleep(0.5)

        LOGGER.info("Finished export job")
        return export_job_arns

    def start(self) -> None:

        """
        Generates, exports, and organizes worlds information into a list of
        dictionaries representing exported jobs, storing it in the shared data
        under the key "worldforge_exported_jobs".

        """
        generation_job_arn = self.__generate_worlds()
        worlds = self.__get_worlds_information(generation_job_arn)
        export_job_arns = self.__export_worlds(worlds, generation_job_arn)

        exported_jobs = []
        for export_arn in export_job_arns:
            exported_jobs.append({
                "destination": self.model.destination,
                "s3_bucket": self.model.s3_bucket,
                "s3_keys": [f"{generation_job_arn}/aws-robomaker-worldforge-export-{export_arn.split('/export-')[1]}.zip"]
            })

        self.shared_data["worldforge_exported_jobs"] = exported_jobs
