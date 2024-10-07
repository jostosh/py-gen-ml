from py_gen_ml.plugin.generator import GenTask

json_schema_gen_tasks = [
    GenTask(obj_path="pgml_out.config_base", obj_name="Optimizer", path="configs/base/schemas/optimizer.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="Data", path="configs/base/schemas/data.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="ConvBlock", path="configs/base/schemas/conv_block.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="LinearBlock", path="configs/base/schemas/linear_block.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="ConvNet", path="configs/base/schemas/conv_net.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="MLP", path="configs/base/schemas/mlp.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="Model", path="configs/base/schemas/model.json"),
    GenTask(obj_path="pgml_out.config_base", obj_name="Project", path="configs/base/schemas/project.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="OptimizerSweep", path="configs/sweep/schemas/optimizer.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="DataSweep", path="configs/sweep/schemas/data.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="ConvBlockSweep", path="configs/sweep/schemas/conv_block.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="LinearBlockSweep", path="configs/sweep/schemas/linear_block.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="ConvNetSweep", path="configs/sweep/schemas/conv_net.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="MLPSweep", path="configs/sweep/schemas/mlp.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="ModelSweep", path="configs/sweep/schemas/model.json"),
    GenTask(obj_path="pgml_out.config_sweep", obj_name="ProjectSweep", path="configs/sweep/schemas/project.json"),
]