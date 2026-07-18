"""Helpers for ``(pgml.kind)`` and shared message-closure utilities."""
from __future__ import annotations

from typing import Set

import networkx
import protogen

from py_gen_ml.extensions_pb2 import MESSAGE_KIND_UNSPECIFIED, MessageKind
from py_gen_ml.plugin.common import get_element_subgraphs, get_extension_value


def get_message_kind(message: protogen.Message) -> MessageKind:
    """Return ``(pgml.kind)`` for ``message``, or ``MESSAGE_KIND_UNSPECIFIED``."""
    kind = get_extension_value(message, 'kind', MessageKind)
    if kind is None:
        return MESSAGE_KIND_UNSPECIFIED
    return kind


def messages_with_kind(
    file: protogen.File,
    kind: MessageKind,
) -> list[protogen.Message]:
    """Return messages in ``file`` whose ``(pgml.kind)`` equals ``kind``."""
    return [message for message in file.messages if get_message_kind(message) == kind]


def collect_message_closure(
    roots: list[protogen.Message],
    file: protogen.File,
) -> Set[protogen.Message]:
    """Messages in ``file`` reachable from ``roots`` via nested message fields."""
    file_messages = set(file.messages)
    to_generate: Set[protogen.Message] = set()
    stack = list(roots)
    while stack:
        message = stack.pop()
        if message not in file_messages or message in to_generate:
            continue
        to_generate.add(message)
        for field in message.fields:
            nested = field.message
            if nested is not None and nested in file_messages:
                stack.append(nested)
    return to_generate


def ordered_messages(
    file: protogen.File,
    messages: Set[protogen.Message],
) -> list[protogen.Message]:
    """Return ``messages`` in topological order within ``file``."""
    ordered: list[protogen.Message] = []
    seen: Set[protogen.Message] = set()
    subgraphs = get_element_subgraphs(file, include_elements={protogen.Kind.MESSAGE})
    for subgraph in subgraphs:
        for node in networkx.topological_sort(subgraph):
            if node in messages and node not in seen:
                ordered.append(node)
                seen.add(node)
    for message in messages:
        if message not in seen:
            ordered.append(message)
    return ordered
