import pytest
from pathfinder_spec import Priority, Task, SharedResource, SystemSpec, default_pathfinder_spec

def test_spec_builds_correctly_n1():
    spec = default_pathfinder_spec(1)
    
    assert spec.n_interferers == 1
    assert len(spec.tasks) == 3
    assert len(spec.resources) == 1
    
    task_names = [t.name for t in spec.tasks]
    assert "bc_sched" in task_names
    assert "ASI_MET" in task_names
    assert "comm_task_1" in task_names
    
    bc_sched = next(t for t in spec.tasks if t.name == "bc_sched")
    asi_met = next(t for t in spec.tasks if t.name == "ASI_MET")
    comm_task = next(t for t in spec.tasks if t.name == "comm_task_1")
    
    assert bc_sched.priority == Priority.HIGH
    assert asi_met.priority == Priority.LOW
    assert comm_task.priority == Priority.MEDIUM
    
    mutex = spec.resources[0]
    assert mutex.name == "info_bus_mutex"
    assert mutex.held_by == "ASI_MET"
    assert mutex.inheritance_enabled is False

def test_spec_builds_correctly_n5():
    spec = default_pathfinder_spec(5)
    
    assert spec.n_interferers == 5
    assert len(spec.tasks) == 7
    
    comm_tasks = [t for t in spec.tasks if t.name.startswith("comm_task")]
    assert len(comm_tasks) == 5
    for ct in comm_tasks:
        assert ct.priority == Priority.MEDIUM

def test_shared_resource_defaults():
    res = SharedResource(name="test_mutex", held_by="TaskA", critical_section_ms=15.0)
    assert res.inheritance_enabled is False
    
    res_enabled = SharedResource(name="test_mutex_2", held_by="TaskB", critical_section_ms=10.0, inheritance_enabled=True)
    assert res_enabled.inheritance_enabled is True
