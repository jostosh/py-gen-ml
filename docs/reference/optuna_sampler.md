# `OptunaSampler`

Visitor that walks a generated sweep config, samples values with an Optuna trial, and returns a patch you can merge onto a base config. Reach for this when running hyperparameter studies without changing your train function.

::: py_gen_ml.OptunaSampler
    options:
        inherited_members:
        - sample
