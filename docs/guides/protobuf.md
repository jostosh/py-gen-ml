# 🧠 Understanding Protobuf in py-gen-ml

## 🌟 Introduction

In this guide, we'll explore the basics of protobuf and how it integrates with the `py-gen-ml` library. Get ready to dive into the world of structured data serialization!

## 🔍 What is Protobuf?

Protobuf (Protocol Buffers) is a language-neutral, platform-neutral, extensible mechanism for serializing structured data. It's a powerful tool for defining data structures and for serializing and deserializing data across different programming languages.

When you install `py-gen-ml`, you get a custom plugin called `protoc-gen-py-ml`. This plugin works behind the scenes when you run `py-gen-ml` to generate code.

### 🛠️ What does py-gen-ml generate?
`py-gen-ml` creates several Pydantic models based on your schema:

1. A 'base' model that closely follows the protobuf schema
2. A 'patch' model for overlaying a base model with modifications
3. A 'sweep' model for defining parameter sweeps over the base model
4. A CLI model that enables automatic argument parsing with nested field support

### 🤔 Why use Protobuf instead of Pydantic directly?
You might wonder why we chose protobuf over direct Pydantic models to act as the source of truth for data structures. Here's why:

- **🧩 Separation of Concerns**: Protobuf separates data structure definition from logic implementation.
- **🔒 Atomic Code Changes**: Generating from protobuf ensures 100% code generation, reducing the risk of diverging code.
- **🌐 Rich Ecosystem**: Protobuf's extensive toolset opens up possibilities for future enhancements.

## 🧱 Key Concepts

Let's break down the main components of Protobuf that you'll need to know:

### 📦 Message
A message is a collection of fields. Here's the basic syntax:

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
    The field number is used to make the serialized representation agnostic to field names. This allows a sender and receiver to change field names independently without breaking the serialized format. If using the protobufs purely for use cases that `py-gen-ml` supports, you can ignore this detail. The main take away is that field numbers are required to be unique within the message.

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

### 🪆 Nesting
Messages can be nested within other messages:

```proto
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

```proto
message Owner {
    string name = 1;
    oneof pet {
        Dog dog = 2;
        Cat cat = 3;
    }
}
```

### 🔁 Repeated
A repeated field contains a list of values:

```proto
message Owner {
    repeated Pet pets = 1;
}
```

### ❓ Optional
An optional field may or may not be present:

```proto
message Pet {
    string name = 1;
    optional string owner_name = 2;
}
```
If a field is optional, it will be translated to a `typing.Optional` type in Pydantic with the default value set to `None`.

### 🎨 Enum
An enum is a type with a predefined set of values:

```proto
enum Color {
    RED = 0;
    GREEN = 1;
    BLUE = 2;
}

message Car {
    Color color = 1;
}
```

### 💬 Adding Comments
Use `//` for comments in your proto files:

```proto
// A car has a color
message Car {
    // The color of the car
    Color color = 1;
}
```

For `py-gen-ml`, leading comments are preserved in the generated code, while trailing comments are not.

## 📚 Further Reading
- [Protobuf in Python](https://protobuf.dev/getting-started/pythontutorial/)
- [Protobuf Documentation](https://developers.google.com/protocol-buffers/docs/proto3)
- [Protobuf Python API Reference](https://googleapis.dev/python/protobuf/latest/)

Now you're equipped with the basics of Protobuf in `py-gen-ml`! Happy coding! 🚀