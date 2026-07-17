# 🧠 Understanding Protobuf in py-gen-ml

## 🌟 Introduction

In `py-gen-ml`, **you author the protobuf schema**. That `.proto` file is the source of truth for your ML configuration. Running `py-gen-ml` feeds it through a deterministic `protoc` plugin (`protoc-gen-py-ml`) that emits the Pydantic models, JSON Schemas, and related tooling you use at train time.

This guide covers the protobuf basics you'll need and how they map into generated code.

## 🔍 What is Protobuf?

Protobuf (Protocol Buffers) is a language-neutral, platform-neutral, extensible mechanism for serializing structured data. It's a powerful tool for defining data structures and for serializing and deserializing data across different programming languages.

When you install `py-gen-ml` via `pip`, you get a protobuf compiler plugin called `protoc-gen-py-ml`. This plugin works behind the scenes when you run `py-gen-ml` to generate code. You do not have to use the `protoc-gen-py-ml` plugin directly.

### 🛠️ What does py-gen-ml generate?
`py-gen-ml` creates several Pydantic models based on your schema:

1. A 'base' model that closely follows the protobuf schema
2. A 'patch' model for overlaying a base model with modifications
3. A 'sweep' model for defining parameter sweeps over the base model
4. A CLI model that enables automatic argument parsing with nested field support

Plus JSON Schemas under `configs/` so your YAML stays validated as you edit.

### 🤔 Why use Protobuf instead of Pydantic directly?
You might wonder why we chose protobuf over direct Pydantic models to act as the source of truth for data structures. Here's why:

- **🧩 Separation of Concerns**: Protobuf separates data structure definition from logic implementation. You maintain one schema. Base, patch, sweep, and CLI shapes stay in sync because they are all generated.
- **🔒 Atomic Code Changes**: Generating from a schema instead of hand-writing parallel models ensures the derived code doesn't drift. That cuts change amplification when nested configs evolve.
- **🌐 Rich Ecosystem**: Protobuf's extensive toolset opens up possibilities for future enhancements (other languages, serialization formats, and so on).

## 🧱 Key Concepts

Let's break down the main components of Protobuf that you'll need to know:

### 📦 Message
A message is a collection of fields, similar to a `dataclass` or a Pydantic `BaseModel`. Here's the basic syntax:

```proto
message MessageName {
    FieldType FieldName = FieldNumber;
}
```

For example:

```proto
message Dog {
    string name = 1;
    uint32 age = 2;
    string breed = 3;
}
```

!!! info
    The term 'message' comes from protobuf's origin in data transfer. The message is serialized before being sent and deserialized after being received. A protobuf compiler generates the code to serialize and deserialize the message for a wide variety of languages.

### 🏷️ Field
A field consists of a type, a name, and a number. The field number is a unique identifier within the message.

!!! info
    The field numbers must be unique. They are used to make the serialized representation agnostic to field names. This allows a sender and receiver to change field names independently without breaking the serialized format. If using the protobufs purely for use cases that `py-gen-ml` supports, you can ignore this detail. The main take away is that field numbers are required to be unique within the message.

### 📊 Built-in Types
Protobuf offers various built-in types:

| Type | Description |
|------|-------------|
| `double` | 64-bit float |
| `float` | 32-bit float |
| `int32` | 32-bit signed integer |
| `int64` | 64-bit signed integer |
| `uint32` | Unsigned 32-bit integer |
| `uint64` | Unsigned 64-bit integer |
| `bool` | Boolean value |
| `string` | String of characters |
| `bytes` | Sequence of bytes |

This list is not exhaustive, but should be enough to use `py-gen-ml` effectively. For more types see [the protobuf docs](https://protobuf.dev/programming-guides/proto3/#scalar).

### 🪆 Nesting
Messages can be nested within other messages:

```proto hl_lines="11"
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

### 🔀 Oneof
A oneof is a set of mutually exclusive fields:

```proto hl_lines="3-6"
message Owner {
    string name = 1;
    oneof pet {
        Dog dog = 2;
        Cat cat = 3;
    }
}
```

See [Unions](oneofs.md) for how `oneof` lands in generated Pydantic models and YAML.

### 🔁 Repeated
A repeated field contains a list of values:

```proto hl_lines="2"
message Owner {
    repeated Pet pets = 1;
}
```

### ❓ Optional
An optional field may or may not be present:

```proto hl_lines="3"
message Pet {
    string name = 1;
    optional string owner_name = 2;
}
```
If a field is optional, it will be translated to a `typing.Optional` type in Pydantic with the default value set to `None`.

### 🎨 Enum
An enum is a type with a predefined set of values:

```proto hl_lines="1-5 8"
enum Color {
    RED = 0;
    GREEN = 1;
    BLUE = 2;
}

message Car {
    Color color = 1;
}
```

See [Enums](enums.md) for YAML usage and how enums show up in patches and sweeps.

### 💬 Adding Comments
Use `//` for comments in your proto files:

```proto hl_lines="1 3"
// A car has a color
message Car {
    // The color of the car
    Color color = 1;
}
```

For `py-gen-ml`, leading comments are preserved in the generated code, while trailing comments are not.

## 📚 Wrapping up

You're now equipped with the protobuf basics for `py-gen-ml`. Next, try the [Quickstart](../quickstart.md) or dig into [YAML configuration](defining_yaml_files.md).

!!! note
    To learn more about the internals of protobuf, here are some optional references to dive into:

    - [Protobuf in Python](https://protobuf.dev/getting-started/pythontutorial/)
    - [Protobuf Documentation](https://developers.google.com/protocol-buffers/docs/proto3)
    - [Protobuf Python API Reference](https://googleapis.dev/python/protobuf/latest/)
