from dataclasses import dataclass, field

@dataclass(frozen=True)
class ReferenceInfo:
    """
    Represents an immutable snapshot of a specific symbol reference 
    tracked between a source module and its target dependency module.
    """
    symbol: str
    source_module: str
    target_module: str


@dataclass(frozen=True)
class ContextResult:
    """
    Represents the calculated cross-file analysis metadata for a single module.
    
    Contains pure calculated arrays reflecting imports, exports, and related 
    modules without mirroring any active indexing states or file architectures.
    """
    module: str
    related_modules: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)