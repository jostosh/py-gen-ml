## Introduction

In this guide, we will go over the basics of protobuf and how to use it with the `py-gen-ml` library.

## Protobuf

Protobuf is a language-neutral, platform-neutral, extensible mechanism for serializing structured data. It is useful for defining data structures and for serializing and deserializing data in a language-agnostic way.

Apart from the official protobuf compiler plugins to generate serialization code and gRPC service definitions, you can define custom plugins that generate code for other purposes. When you install `py-gen-ml`, you install a plugin called `protoc-gen-py-ml` that is used under the hood when running `py-gen-ml` to generate code.

### What is generated?
`py-gen-ml` generates several variations of your schema as Pydantic models:

1. A Pydantic model that follows the protobuf schema as closely as possible (called a 'base')
2. A Pydantic model that allows for overlaying a base model with a patch model (called a 'patch')
3. A Pydantic model that allows for defining sweeps over the base model (called a 'sweep')
4. A Pydantic model that enables automatic CLI argument parsing with CLI options that are automatically shortened yet map to fields that can be nested arbitrarily deep

### Why not generate code from Pydantic base models?
One might wonder why we chose to depend on protobuf instead of using Pydantic models directly to generate code. There are several reasons:

- **Separating concerns**: By using protobuf, we separate the concerns of defining data structures from the concerns of defining the logic (validating YAMLs, sweeps, CLI argument parsers, etc.).

- **Atomic code changes**: If we were to use a Pydantic base model directly to generate other base models, there's a larger risk of the base models diverging from the generated code. If generating from protobuf, 100% of the code is generated and so there's no risk of diverging code. Note that it is still your responsibility to regenerate code on updates to the protobuf file.

- **A rich ecosystem**: Protobuf has a rich ecosystem of tools and libraries that are widely used in the industry. This would enable generating more than just the tooling in `py-gen-ml`. For example, one could imagine generating a Pydantic model of the data structure which could be used for things like auto-generating documentation, auto-generating API endpoints, etc. As of the current version of `py-gen-ml`, we have not yet leveraged the full potential of this.

## Concepts
Protobuf allows us to focus defining data structures. There are a few concepts to familiarize yourself with:

- `message`: A message is a collection of fields.
- `field`: A field is a name-value pair.
- `oneof`: A oneof is a collection of fields that are mutually exclusive.
- `repeated`: A repeated field is a field that contains a list of values.
- `optional`: An optional field is a field that may or may not be present.
- `enum`: An enum is a type that can take one of a set of named values.

### Message
The message is defined through the following syntax:

```
message MessageName {
    // Field definitions
    FieldType FieldName = FieldNumber;
}
```

For example, a simple message for a `Dog` could look like this:

```proto
message Dog {
    string name = 1;
    uint32 age = 2;
    string breed = 3;
}
```

!!! note
    The name 'message' stems from the fact that protobuf is designed to streamline serialization and deserialization of data where the serializer often is on a different machine than the deserializer and the data needs to be transferred as a message.



### Field
A field takes a type, a name, and a number. The type is usually just a built-in like `int`, `float`, `string`, etc. You can also use enums and other messages as field types. More on that later.

The _field number_ (e.g. `1`, `2`, `3` in the example above) is used to identify the field in the message and must be unique within the message. The syntax might be somewhat confusing at first as the number seems to be assigned to the field as a value. You should instead think of the field number as an identifier for the field.

!!! note
    The identifier is used to make the serialized representation agnostic to field names. This allows a 'server' and 'client' (or 'writer' and 'reader') change field names independently.

    Outside of `py-gen-ml`, field numbers are thus used to make such updates to the schema forward and backward compatible. Currently, `py-gen-ml` is not leaning into this feature. Hence, for learning purposes, you can think of the field number as an identifier for the field and ignore the details about how it is used to make the serialized representation agnostic to field names.

    Over time, you will most likely learn to ignore the number when reading proto files anyway.

### Built-in types
The table below shows the built-in types that can be used in a protobuf message.

| Type      | Description |
| ----------- | ----------- |
| `double`      | A 64-bit floating point number |
| `float`      | A 32-bit floating point number |
| `int32`      | A 32-bit signed integer |
| `int64`      | A 64-bit signed integer |
| `uint32`      | An unsigned 32-bit integer |
| `uint64`      | An unsigned 64-bit integer |
| `bool`      | A boolean value |
| `string`      | A string of characters |
| `bytes`      | A sequence of bytes |

!!! note
    The table is not exhaustive. For a full list of built-in types, see the [Protobuf documentation](https://developers.google.com/protocol-buffers/docs/proto3#scalar).

### Nesting
Messages can use other messages as fields. This allows for nesting of messages.

```proto linenums="1" hl_lines="11"
message Address {
    string street = 1;
    string city = 2;
    string state = 3;
    string zip = 4;
}

message Person {
    string name = 1;
    uint32 age = 2;
    Address address = 3;
}
```
### Oneof
A oneof is a collection of fields that are mutually exclusive. This means that only one field can be set at a time. If you need to use multiple fields, you can use a oneof.

```proto linenums="1" hl_lines="7-10"
message Pet {
    string name = 1;
}

message Owner {
    string name = 1;
    oneof pet {
        Dog dog = 2;
        Cat cat = 3;
    }
}
```

### Repeated
A repeated field is a field that contains a list of values.

```proto linenums="1" hl_lines="6"
message Pet {
    string name = 1;
}

message Owner {
    repeated Pet pets = 1;
}
```

### Optional
An optional field is a field that may or may not be present. In the case of `py-gen-ml`, this will be translated to a `typing.Optional` type
and the default value will be `None`.

```proto linenums="1" hl_lines="3"
message Pet {
    string name = 1;
    optional string owner_name = 2;
}
```


### Enum
An enum is a type that can take one of a set of named values..

```proto linenums="1" hl_lines="1-5 8"
enum Color {
    RED = 0;
    GREEN = 1;
    BLUE = 2;
}

message Car {
    Color color = 1;
}
```

### Adding comments
Comments can be added to a proto file using the `//` syntax.

```proto linenums="1" hl_lines="1 3"
// A car has a color
message Car {
    // The color of the car
    Color color = 1;
}
```

Leading comments will be preserved in the generated code, while trailing comments will not.

## Further reading
- [Protobuf in Python](https://protobuf.dev/getting-started/pythontutorial/)
- [Protobuf documentation](https://developers.google.com/protocol-buffers/docs/proto3)
- [Protobuf Python API Reference](https://googleapis.dev/python/protobuf/latest/)
