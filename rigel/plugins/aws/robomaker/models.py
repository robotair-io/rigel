from pydantic import BaseModel, Extra, Field, validator
from rigel.exceptions import InvalidValueError
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

DEFAULT_ROBOT_APPLICATION_NAME: str = 'rigel_robomaker_robot_application'
DEFAULT_SIMULATION_APPLICATION_NAME: str = 'rigel_robomaker_simulation_application'


class VPCConfig(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a model for configuring a Virtual Private Cloud (VPC). It consists of
    lists of subnets and security groups, as well as a boolean option to assign a
    public IP address. The class is designed to restrict extra properties from
    being set.

    Attributes:
        subnets (List[str]): Required (not explicitely stated, but implied due to
            inheritance from `BaseModel`). It represents a list of subnet IDs or
            names that can be used for resources within the VPC.
        securityGroups (List[str]): Alias for the attribute `security_groups`.
        assignPublicIp (bool): Initially set to False by default. It can be
            optionally assigned a value of True during object creation, indicating
            whether public IP should be assigned.

    """
    subnets: List[str]
    securityGroups: List[str] = Field(alias='security_groups')

    # Optional fields
    assignPublicIp: bool = Field(alias='assign_public_ip', default=False)


class Tool(BaseModel):

    """
    Validates and configures a tool's settings, enforcing required fields for name
    and command, while allowing optional fields with default values. It checks the
    'exitBehavior' field against predefined values ('FAIL', 'RESTART') to ensure
    validity.

    Attributes:
        name (str): A required field, meaning it must be provided when creating
            an instance of the `Tool` class. It represents a string value that
            corresponds to the name of the tool.
        command (str): Required by default. It does not have any specific alias
            or default value, implying that it must be provided when creating a
            new instance of the `Tool` class.
        exitBehavior (str): Optional by default. It can take two values, 'FAIL'
            or 'RESTART', and defaults to 'RESTART'. Validation ensures that any
            provided value matches one of these allowed options.
        streamOutputToCloudWatch (bool): Optional by default. Its default value
            is False, and it can be overridden during object creation. It allows
            streaming output to Cloud Watch.
        streamUI (bool): Optional by default, meaning it can be omitted when
            creating a new instance of `Tool`. It represents whether to stream the
            UI output or not.

    """

    class Config:
        """
        Configures serialization options for a Python application, specifically
        for JSON-based APIs. It sets two properties: `allow_population_by_field_name`
        to allow population by field name and `extra` to forbid extra fields in
        the output.

        Attributes:
            allow_population_by_field_name (bool): Set to `True`. It allows fields
                to be populated by using a field name that matches the variable
                name in the Python code, rather than requiring exact matching.
            extra (Extra): Set to `forbid`, which means that any additional fields
                in the request data will be rejected, rather than being ignored
                or accepted as default values.

        """
        allow_population_by_field_name = True
        extra = Extra.forbid

    # Required fields
    name: str
    command: str

    # Optional fields.
    exitBehavior: str = Field(alias='exit_behaviour', default='RESTART')
    streamOutputToCloudWatch: bool = Field(alias='stream_output_to_cloud_watch', default=False)
    streamUI: bool = Field(alias='stream_ui', default=False)

    @validator('exitBehavior')
    def validate_exit_behavior(cls, exitBehavior: str) -> str:
        """
        Validates an input string representing an exit behavior, ensuring it matches
        either 'FAIL' or 'RESTART'. If not valid, it raises an InvalidValueError;
        otherwise, returns the validated value.

        Args:
            exitBehavior (str): Validated to ensure it has one of two specific
                values, 'FAIL' or 'RESTART'. If not, an error is raised.

        Returns:
            str: Either 'FAIL' or 'RESTART' if the input meets the condition, and
            raises an error otherwise.

        """
        if exitBehavior not in ['FAIL', 'RESTART']:
            raise InvalidValueError(field='exitBehavior', value=exitBehavior)
        return exitBehavior


class RobotApplication(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a model for robot applications. It contains attributes for ECR, command,
    name, environment, ports, streamUI, and tools. The `BaseModel` is inherited
    from Pydantic's BaseModel to enable validation of the input data. Extra
    parameters are forbidden in this model.

    Attributes:
        ecr (str): A required field for this model, as indicated by its presence
            in the class definition.
        command (List[str]): A collection of strings representing commands.
        name (str): Set to `DEFAULT_ROBOT_APPLICATION_NAME` by default. It represents
            a unique name for the robot application.
        environment (List[str]): Initialized with an empty list by default. It
            allows for a variable number of strings to be added, representing the
            environment settings or conditions for the robot application.
        ports (List[Tuple[int, int]]): Optional by default. It represents a list
            of tuples where each tuple contains two integers representing start
            and end port numbers for a specific communication protocol.
        streamUI (bool): Alias of 'stream_ui'. It has a default value of False,
            indicating that by default, the stream UI is not enabled for this robot
            application.
        tools (List[Tool]): Not initialized with any value by default. It means
            this attribute requires a non-empty list of `Tool` objects when creating
            an instance of `RobotApplication`.

    """
    ecr: str
    command: List[str]

    # Optional fields
    name: str = DEFAULT_ROBOT_APPLICATION_NAME
    environment: List[str] = []
    ports: List[Tuple[int, int]] = []
    streamUI: bool = Field(alias='stream_ui', default=False)
    tools: List[Tool] = []


class SimulationApplication(RobotApplication):

    # Optional fields
    """
    Defines a simulation application that inherits from `RobotApplication`. It
    contains properties for the name and world configurations, which is a list of
    dictionaries representing different worlds. The `world_configs` field is an
    alias for the list with a default value of an empty list.

    Attributes:
        name (str): Set to a default value specified by `DEFAULT_SIMULATION_APPLICATION_NAME`.
            This name is used to identify the application.
        worldConfigs (List[Dict[Literal["world"], str]]): Alias'd as 'world_configs'.
            It has a default value of an empty list.

    """
    name: str = DEFAULT_SIMULATION_APPLICATION_NAME
    worldConfigs: List[Dict[Literal["world"], str]] = Field(alias='world_configs', default=[])


# class WorldForgeExportedJob(BaseModel, extra=Extra.forbid):

#     # Required field
#     destination: str
#     s3Bucket: str = Field(alias='s3_bucket')
#     s3Keys: str = Field(alias='s3_keys')


class DataSource(BaseModel, extra=Extra.forbid):
    """
    Defines a data source model with required fields for destination, name, and
    S3 bucket/keys. It also specifies a default type as "File" and validates it
    to be one of three allowed types: "Prefix", "Archive", or "File".

    Attributes:
        destination (str): Required.
        name (str): Required, as specified by its presence without a default value
            assigned to it.
        s3Bucket (str): Initialized with a default value. It has an alias 's3_bucket',
            indicating that it can also be referred to as 's3_bucket' when accessing
            or validating the attribute.
        s3Keys (List[str]): Aliased as "s3_keys". It represents a list of S3 keys
            associated with the data source, which is optional since it's not
            marked as required.
        type (str): Initialized with a default value of 'File'. It can be changed,
            but it must be one of ['Prefix', 'Archive', 'File'].

    """

    # Required field
    destination: str
    name: str
    s3Bucket: str = Field(alias='s3_bucket')
    s3Keys: List[str] = Field(alias='s3_keys')

    # Optional fields:
    type: str = 'File'

    @validator('type')
    def validate_data_source_type(cls, ds_type: str) -> str:
        """
        Validates the 'type' field of the data source. If the type is not one of
        'Prefix', 'Archive', or 'File', it raises an InvalidValueError; otherwise,
        it returns the validated type.

        Args:
            ds_type (str): Specified as a type hint. It represents the data source
                type, which should be one of 'Prefix', 'Archive', or 'File'.

        Returns:
            str: Either the validated `ds_type` or None, if the validation fails
            and an exception is raised.

        """
        if ds_type not in ['Prefix', 'Archive', 'File']:
            raise InvalidValueError(field='type', value=ds_type)
        return ds_type

    # TODO: add validator to ensure that field 'destination'
    # is set according to the value of field 'type'


class Compute(BaseModel, extra=Extra.forbid):
    """
    Defines a schema for computing resources, inheriting from `BaseModel`. It has
    three fields: `computeType`, specifying CPU or GPU/CPU combination; `gpuUnitLimit`
    and `simulationUnitLimit`, both integers representing respective limits. The
    `extra=Extra.forbid` parameter disallows additional properties beyond these
    defined fields.

    Attributes:
        computeType (Union[Literal['CPU'], Literal['GPU_AND_CPU']]): Aliased as
            'compute_type'. It can take two values: 'CPU' or 'GPU_AND_CPU',
            indicating whether the computation is done on CPU only or both GPU and
            CPU.
        gpuUnitLimit (int): Alias for the field with the same name. It represents
            the limit on GPU units.
        simulationUnitLimit (int): Aliased as 'simulation_unit_limit'.

    """

    computeType: Union[Literal['CPU'], Literal['GPU_AND_CPU']] = Field(alias='compute_type')
    gpuUnitLimit: int = Field(alias='gpu_unit_limit')
    simulationUnitLimit: int = Field(alias='simulation_unit_limit')


class PluginModel(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a schema for a plugin configuration model, which includes properties
    such as IAM role, robot application, simulation duration, and VPC configuration.
    It also allows optional fields like output location, worldforge exported job,
    simulation application, and compute settings.

    Attributes:
        iam_role (str): Required, as indicated by its presence in the class
            definition without any specified default value or `Optional` indicator.
        robot_application (Optional[RobotApplication]): Optional, meaning it can
            be assigned a value or left as None.
        simulation_application (Optional[SimulationApplication]): Optional, meaning
            it can be set to None or any value of type SimulationApplication.
        worldforge_exported_job (Optional[Dict[str, Any]]): Optional. It can hold
            a dictionary with any key-value pairs representing an exported job
            from WorldForge.
        output_location (Optional[str]): Optional, meaning it can be either present
            with a value or absent. It represents a possible output location for
            simulation results.
        simulation_duration (int): 300 by default, indicating the duration of a
            simulation in seconds.
        vpc_config (Optional[VPCConfig]): Optional, meaning it can be missing or
            None.
        compute (Optional[Compute]): Optional, meaning it can be either set or not
            set. When set, its value is an instance of the Compute class.
        data_sources (List[DataSource]): Initialized with an empty list. It allows
            multiple data sources to be defined, each being a `DataSource` object.

    """
    iam_role: str

    # Optional fields
    robot_application: Optional[RobotApplication] = None
    simulation_application: Optional[SimulationApplication] = None
    worldforge_exported_job: Optional[Dict[str, Any]] = None
    output_location: Optional[str] = None
    simulation_duration: int = 300  # seconds
    vpc_config: Optional[VPCConfig] = None
    compute: Optional[Compute] = None
    data_sources: List[DataSource] = []
