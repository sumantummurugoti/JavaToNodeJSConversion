"""
Data Models
Dataclasses for storing analysis results
"""

from dataclasses import dataclass, asdict
from typing import List


@dataclass
class MethodInfo:
    """Information about a method"""
    name: str
    signature: str
    description: str
    complexity: str


@dataclass
class ModuleInfo:
    """Information about a Java module/class"""
    name: str
    type: str  # Controller, Service, DAO, Model, etc.
    description: str
    file_path: str
    methods: List[MethodInfo]
    dependencies: List[str]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'file_path': self.file_path,
            'methods': [asdict(m) for m in self.methods],
            'dependencies': self.dependencies
        }
