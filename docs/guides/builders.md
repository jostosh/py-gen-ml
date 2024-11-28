# 🏭 Factories

## 🪄 Generated Factory Methods
Occasionally, you have enough information to instantiate a class from a configuration object immediately. `py-gen-ml` allows you to generate factory methods in such cases. The factory methods unpack the message fields into keyword arguments and then instantiate an object.

To specify a factory method for a message, you can use the `(pgml.factory)` option. For example:

```proto linenums="1" hl_lines="6-7 12"
--8<-- "docs/snippets/proto/builder_demo.proto"
```

The generated code will look like this:

```python { linenums="1" hl_lines="23-30" .generated-code }
--8<-- "docs/snippets/src/pgml_out/builder_demo_base.py"
```

Notice the `build` method. This method is automatically generated for you. It unpacks the message fields into keyword arguments and then instantiates the class.

In your experiment code, you can now call the `build` method to instantiate the class:

```python linenums="1" hl_lines="8"
import torch

from pgml_out.builder_demo_base import MLP

if __name__ == "__main__":
    mlp_config = MLP.from_yaml("configs/base/mlp.yaml")

    layers = [layer.build() for layer in mlp_config.layers]
    mlp = torch.nn.Sequential(*layers)
```

## 🧱 Using custom classes

The builder extension can be used for any class, not just PyTorch classes. You can use it to instantiate any class that you have access to.

For example, let's say you have a custom class that you want to instantiate. You can do this:

```python
# src/example_project/modules.py
import torch.nn


class LinearBlock(torch.nn.Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True, dropout: float = 0.0, activation: str = "relu"):
        super().__init__()
        self.linear = torch.nn.Linear(in_features, out_features, bias=bias)
        self.dropout = torch.nn.Dropout(dropout)
        self.activation = torch.nn.ReLU() if activation == "relu" else torch.nn.GELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.activation(self.linear(x)))
```

And then define the following proto:

```proto linenums="1" hl_lines="6 11"
--8<-- "docs/snippets/proto/builder_custom_class_demo.proto"
```

The generated code will look like this:

```python { linenums="1" hl_lines="29-38" .generated-code }
--8<-- "docs/snippets/src/pgml_out/builder_custom_class_demo_base.py"
```

## 💥 Expanding fields as varargs

You can also expand fields as varargs. This is useful if you have a list of arguments that you want to pass to the builder. For example, let's say you have a custom class that you want to instantiate. You can use the
`(pgml.as_varargs)` option to expand the fields as varargs. For example:

```proto linenums="1" hl_lines="24"
--8<-- "docs/snippets/proto/builder_varargs_demo.proto"
```

The generated code will look like this:

```python { linenums="1" hl_lines="42-44" .generated-code }
--8<-- "docs/snippets/src/pgml_out/builder_varargs_demo_base.py"
```

## 🐣 Nesting factories

As you may have noticed, factories can also be nested. In the section on varargs, we see that the build method in `MLP` takes a varargs of `Linear` objects that are also instantiated with a factory. Nesting with factories can streamline instantiation of complex objects, but it also creates a tighter coupling between your schema and the objects that are created.

Usually, it is best to use factories for objects that don't need other factories for their fields. In other words, you should nest factories sparingly.
