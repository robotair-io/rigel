from pydantic import BaseModel, Extra


class PluginModel(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a data structure for storing plugin configuration information, including
    IAM role, template ARN, S3 bucket, and destination. It also includes two
    counters, `floor_plan_count` and `interior_count`, initially set to 1. This
    class likely serves as a template for creating plugins in an application.

    Attributes:
        iam_role (str): Part of the model that represents a plugin instance. It
            likely specifies the IAM role used by the plugin for its operations.
        template_arn (str): A string representing the Amazon Resource Name (ARN)
            of a CloudFormation template.
        s3_bucket (str): Assigned a default value representing a bucket name.
        destination (str): Part of the base class definition. It represents a
            string value that is expected to be provided by users when creating
            instances of this model.
        floor_plan_count (int): 1 by default. This suggests that it represents a
            count of floor plans, with a default value of 1. The use of an integer
            data type implies that this count can be incremented or decremented
            as needed.
        interior_count (int): 1 by default, implying a single value for this count.
            It can be modified by assigning another integer value to it.

    """
    iam_role: str
    template_arn: str
    s3_bucket: str
    destination: str

    # Optional fields.
    floor_plan_count: int = 1
    interior_count: int = 1
