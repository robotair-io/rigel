from jinja2 import Template
from pkg_resources import resource_string
from rigel.models import DockerSection


class Renderer:
    """
    Renders a template file based on a given configuration and saves it to an
    output file. It uses the Jinja2 templating engine to replace placeholders with
    actual values from the configuration dictionary.

    Attributes:
        configuration_file (DockerSection): Initialized during object creation
            with a specified configuration file. It represents a configuration
            file for rendering templates.

    """

    def __init__(self, configuration_file: DockerSection) -> None:
        """
        :type configuration_file: rigel.models.DockerSection
        :param configuration_file: An aggregator of information about the containerization of the ROS application.
        """
        self.configuration_file = configuration_file

    def render(self, template: str, output: str) -> None:
        """
        Generates a Dockerfile from a template and writes it to an output file
        based on a configuration file, replacing placeholders with actual values.

        Args:
            template (str): Expected to be a string representing the name of a
                template file located in the 'assets/templates/' directory.
            output (str): Used to specify the path or name of the file where the
                rendered template will be written.

        """
        # Open file template.
        dockerfile_template = resource_string(__name__, f'assets/templates/{template}').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open(output, 'w+') as output_file:
            output_file.write(dockerfile_templater.render(configuration=self.configuration_file.dict()))
