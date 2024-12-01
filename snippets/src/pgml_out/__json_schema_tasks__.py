from py_gen_ml.plugin.generator import GenTask

json_schema_gen_tasks = [
    GenTask(obj_path="pgml_out.advanced_base", obj_name="LinearBlock", path="docs/snippets/configs/base/schemas/linear_block.json"),
    GenTask(obj_path="pgml_out.advanced_base", obj_name="Optimizer", path="docs/snippets/configs/base/schemas/optimizer.json"),
    GenTask(obj_path="pgml_out.advanced_base", obj_name="MLP", path="docs/snippets/configs/base/schemas/mlp.json"),
    GenTask(obj_path="pgml_out.advanced_base", obj_name="Training", path="docs/snippets/configs/base/schemas/training.json"),
    GenTask(obj_path="pgml_out.advanced_patch", obj_name="LinearBlockPatch", path="docs/snippets/configs/patch/schemas/linear_block.json"),
    GenTask(obj_path="pgml_out.advanced_patch", obj_name="OptimizerPatch", path="docs/snippets/configs/patch/schemas/optimizer.json"),
    GenTask(obj_path="pgml_out.advanced_patch", obj_name="MLPPatch", path="docs/snippets/configs/patch/schemas/mlp.json"),
    GenTask(obj_path="pgml_out.advanced_patch", obj_name="TrainingPatch", path="docs/snippets/configs/patch/schemas/training.json"),
    GenTask(obj_path="pgml_out.advanced_sweep", obj_name="LinearBlockSweep", path="docs/snippets/configs/sweep/schemas/linear_block.json"),
    GenTask(obj_path="pgml_out.advanced_sweep", obj_name="OptimizerSweep", path="docs/snippets/configs/sweep/schemas/optimizer.json"),
    GenTask(obj_path="pgml_out.advanced_sweep", obj_name="MLPSweep", path="docs/snippets/configs/sweep/schemas/mlp.json"),
    GenTask(obj_path="pgml_out.advanced_sweep", obj_name="TrainingSweep", path="docs/snippets/configs/sweep/schemas/training.json"),
]