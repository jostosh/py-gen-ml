import protogen

from py_gen_ml.plugin.generator import Generator, GenTask


class JsonSchemaTaskGenerator(Generator):
    """
    A generator that creates tasks for generating JSON schema from a set of objects.

    The generated file will be imported by the py-gen-ml CLI to generate JSON schema for the given objects.
    """

    def __init__(self, gen: protogen.Plugin, tasks: list[GenTask]) -> None:
        """
        Initialize the JsonSchemaTaskGenerator.

        Args:
            gen (protogen.Plugin): The plugin instance.
            tasks (List[GenTask]): The list of tasks to generate.
        """
        super().__init__(gen)
        self._tasks = tasks

    def generate_code(self) -> None:
        """Generate the code for the JSON schema tasks."""
        g = self._gen.new_generated_file('__json_schema_tasks__.py', protogen.PyImportPath('__json_schema_tasks__'))
        g.P('from py_gen_ml.plugin.generator import GenTask')
        g.P()
        g.P('json_schema_gen_tasks = [')
        g.set_indent(4)
        for task in self._tasks:
            g.P(f"GenTask(obj_path=\"{task.obj_path}\", obj_name=\"{task.obj_name}\", path=\"{task.path}\"),")
        g.set_indent(0)
        g.P(']')

    def _generate_code_for_file(self, file: protogen.File) -> None:
        pass
