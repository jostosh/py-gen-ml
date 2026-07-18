"""Registry for code generators.

The :class:`GeneratorRegistry` is the extension point for adding new code
generators to the ``protoc-gen-py-ml`` plugin. Built-in generators (base, patch,
sweep, cli_args) are registered by :func:`default_registry`. Third-party
packages can ship additional generators by exposing a :class:`GeneratorSpec` (or
a zero-argument callable returning one) under the ``py_gen_ml.generators``
entry-point group.

Example (third-party package's ``pyproject.toml``)::

    [project.entry-points."py_gen_ml.generators"]
    lancedb_schema = "py_gen_ml_lancedb:lancedb_schema_spec"

The plugin runs every registered generator unless the user passes
``enabled_generators=...`` (semicolon-separated names) as a plugin parameter, in
which case only the named generators run.
"""
from __future__ import annotations

import importlib.metadata
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

import protogen

from py_gen_ml.logging.setup_logger import setup_logger
from py_gen_ml.plugin.generator import Generator

logger = setup_logger(__name__)

ENTRY_POINT_GROUP = 'py_gen_ml.generators'

GeneratorFactory = Callable[[protogen.Plugin], Generator]


@dataclass(frozen=True)
class GeneratorSpec:
    """Descriptor for a registered generator.

    Attributes:
        name: Stable identifier; used for ``--generators`` selection.
        factory: Callable invoked with the active :class:`protogen.Plugin` to
            construct the generator instance.
        enabled_by_default: When ``False``, the generator only runs if it is
            explicitly listed in ``enabled_generators``.
        description: Optional human-readable description (surfaced in errors).
    """

    name: str
    factory: GeneratorFactory
    enabled_by_default: bool = True
    description: str = ''


class GeneratorRegistry:
    """Ordered registry of :class:`GeneratorSpec` instances.

    Insertion order is preserved so that, when no explicit selection is given,
    generators run in the order they were registered. ``register`` overrides any
    previous spec with the same name.
    """

    def __init__(self) -> None:
        self._specs: dict[str, GeneratorSpec] = {}

    def register(self, spec: GeneratorSpec) -> None:
        if not spec.name:
            raise ValueError('GeneratorSpec.name must be a non-empty string')
        if spec.name in self._specs:
            logger.debug('Overriding generator %r already registered', spec.name)
        self._specs[spec.name] = spec

    def unregister(self, name: str) -> None:
        self._specs.pop(name, None)

    def get(self, name: str) -> GeneratorSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            available = ', '.join(sorted(self._specs)) or '<none>'
            raise KeyError(f'Unknown generator {name!r}. Registered: {available}') from exc

    def list(self) -> List[GeneratorSpec]:
        return list(self._specs.values())

    def names(self) -> List[str]:
        return list(self._specs)

    def build_active(
        self,
        plugin: protogen.Plugin,
        *,
        enabled: Optional[Iterable[str]] = None,
    ) -> List[Generator]:
        """Instantiate the generators that should run for this invocation.

        When ``enabled`` is ``None`` every spec with ``enabled_by_default=True``
        is constructed. Otherwise only the named specs are constructed, in the
        order they appear in ``enabled``.
        """
        if enabled is None:
            specs = [s for s in self._specs.values() if s.enabled_by_default]
        else:
            specs = [self.get(name) for name in enabled]
        return [spec.factory(plugin) for spec in specs]


def _load_builtin_specs() -> List[GeneratorSpec]:
    # Imported lazily to avoid a circular import: the generators import
    # `Generator`, which lives next to this module.
    from py_gen_ml.plugin.base_model_generator import base_spec, patch_spec
    from py_gen_ml.plugin.bentoml_generator import bentoml_spec
    from py_gen_ml.plugin.cli_args_generator import cli_args_spec
    from py_gen_ml.plugin.lancedb_generator import lancedb_spec
    from py_gen_ml.plugin.litserve_generator import litserve_spec
    from py_gen_ml.plugin.sweep_model_generator import sweep_spec

    return [
        base_spec,
        patch_spec,
        sweep_spec,
        cli_args_spec,
        lancedb_spec,
        bentoml_spec,
        litserve_spec,
    ]


def _load_entry_point_specs() -> List[GeneratorSpec]:
    specs: List[GeneratorSpec] = []
    try:
        # Python 3.10+ accepts the `group` keyword.
        eps = importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)  # type: ignore[call-arg]
    except TypeError:
        # Python 3.9 returns a SelectableGroups dict.
        eps = importlib.metadata.entry_points().get(ENTRY_POINT_GROUP, [])  # type: ignore[assignment]
    for ep in eps:
        try:
            obj = ep.load()
        except Exception:  # pragma: no cover - defensive isolation
            logger.exception('Failed to load generator entry point %r; skipping', ep.name)
            continue
        spec = obj() if callable(obj) and not isinstance(obj, GeneratorSpec) else obj
        if not isinstance(spec, GeneratorSpec):
            logger.warning(
                'Entry point %r resolved to %r, which is not a GeneratorSpec; skipping',
                ep.name,
                type(spec).__name__,
            )
            continue
        specs.append(spec)
    return specs


def default_registry(*, include_entry_points: bool = True) -> GeneratorRegistry:
    """Build a registry pre-populated with the built-in generators.

    When ``include_entry_points`` is ``True`` (the default) the registry also
    discovers third-party generators via the ``py_gen_ml.generators`` entry
    point group. Built-ins always win over entry points with the same name.
    """
    registry = GeneratorRegistry()
    if include_entry_points:
        for spec in _load_entry_point_specs():
            registry.register(spec)
    for spec in _load_builtin_specs():
        registry.register(spec)
    return registry


__all__ = [
    'ENTRY_POINT_GROUP',
    'GeneratorFactory',
    'GeneratorRegistry',
    'GeneratorSpec',
    'default_registry',
]
