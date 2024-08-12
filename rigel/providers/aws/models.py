from pydantic import BaseModel, Extra, validator
from rigel.exceptions import InvalidValueError
from typing import Any, List, Optional


class AWSProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a data model for Amazon Web Services (AWS) provider configuration. It
    has properties for AWS access key ID, secret access key, region name, and list
    of supported services. The `validate_services` method checks if the service
    list is not empty.

    Attributes:
        aws_access_key_id (str): Required.
        aws_secret_access_key (str): Part of the AWS provider model definition.
            It represents a sensitive secret key for accessing Amazon Web Services
            (AWS) resources.
        region_name (str): A mandatory field in this model. It represents the
            region name where AWS resources are located, required for interacting
            with Amazon Web Services.
        services (List[str]): Validated using a validator function, ensuring it
            contains at least one service name string. If no services are provided,
            it raises an InvalidValueError.
        ecr_servers (List[str]): Initialized with an empty list. This means it can
            store a collection of strings representing ECR server names.

    """
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
    services: List[str]

    # Optional fields
    ecr_servers: List[str] = []

    @validator('services')
    def validate_services(cls, services: List[str]) -> List[str]:
        """
        Validates the input services list. If it's empty, it raises an InvalidValueError;
        otherwise, it returns the original list. This function is typically used
        for data validation during model creation or update operations in an application.

        Args:
            services (List[str]): Expected to be a list of strings, representing
                various services.

        Returns:
            List[str]: An unchanged list of service strings, if no error is raised.
            If the input list is empty, it raises an exception instead of returning
            anything.

        """
        if not services:
            raise InvalidValueError(field='services', value=services)
        return services


class AWSProviderOutputModel(BaseModel, extra=Extra.forbid):

    # Optional fields
    """
    Defines a data model for output from an AWS provider. It inherits from `BaseModel`
    and has one attribute, `robomaker_client`, which is optional (can be `None`)
    and of type `Any`. This class ensures that the provided data conforms to its
    expected structure.

    Attributes:
        robomaker_client (Optional[Any]): Initialized as None. This means that
            this attribute can either be a value of any data type or it can be
            None, indicating that no value has been assigned to it yet.

    """
    robomaker_client: Optional[Any] = None
