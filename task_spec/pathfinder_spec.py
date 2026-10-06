from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class Task:
    name: str
    priority: Priority
    period_ms: float
    exec_ms: float
    deadline_ms: float

@dataclass
class SharedResource:
    name: str
    held_by: Optional[str]
    critical_section_ms: float
    inheritance_enabled: bool = False

@dataclass
class SystemSpec:
    tasks: List[Task]
    resources: List[SharedResource]
    n_interferers: int

def default_pathfinder_spec(n_interferers: int) -> SystemSpec:
    bc_sched = Task(
        name="bc_sched",
        priority=Priority.HIGH,
        period_ms=125.0,
        exec_ms=10.0,
        deadline_ms=125.0
    )
    
    asi_met = Task(
        name="ASI_MET",
        priority=Priority.LOW,
        period_ms=1000.0,
        exec_ms=50.0,
        deadline_ms=1000.0
    )
    
    tasks = [bc_sched, asi_met]
    
    for i in range(n_interferers):
        comm_task = Task(
            name=f"comm_task_{i+1}",
            priority=Priority.MEDIUM,
            period_ms=250.0,
            exec_ms=25.0,
            deadline_ms=250.0
        )
        tasks.append(comm_task)
        
    info_bus_mutex = SharedResource(
        name="info_bus_mutex",
        held_by="ASI_MET",
        critical_section_ms=30.0,
        inheritance_enabled=False
    )
    
    resources = [info_bus_mutex]
    
    return SystemSpec(
        tasks=tasks,
        resources=resources,
        n_interferers=n_interferers
    )
