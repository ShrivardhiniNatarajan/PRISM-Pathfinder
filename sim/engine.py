import simpy
from typing import Dict
from task_spec.pathfinder_spec import SystemSpec, Priority

class Job:
    def __init__(self, task_name, base_priority, exec_ms, deadline_abs):
        self.task_name = task_name
        self.base_priority = base_priority
        self.eff_priority = base_priority
        self.remaining_exec = exec_ms
        self.deadline_abs = deadline_abs
        
        self.wants_mutex = False
        self.holds_mutex = False
        
        self.mutex_req_at = 0
        self.mutex_duration = 0
        if task_name == "ASI_MET":
            self.mutex_req_at = 10
            self.mutex_duration = 30
        elif task_name == "bc_sched":
            self.mutex_req_at = 2
            self.mutex_duration = 6
            
        self.started_waiting_mutex = None
        self.blocking_time = 0

class Simulator:
    def __init__(self, spec: SystemSpec, condition: str, duration: int = 10000):
        self.env = simpy.Environment()
        self.spec = spec
        self.condition = condition
        self.duration = duration
        
        self.ready_queue = []
        self.mutex_holder = None
        self.mutex_waiters = []
        
        self.missed_deadlines = 0
        self.worst_case_blocking_bc = 0
        self.total_blocking_bc = 0
        self.bc_jobs_blocked = 0
        self.inheritance_active_ms = 0
        
        # Calculate PCP Ceiling
        # In our simplified model, info_bus_mutex is used by ASI_MET and bc_sched.
        # Thus its ceiling is HIGH.
        self.mutex_ceiling = Priority.HIGH
        
        for t in spec.tasks:
            self.env.process(self.task_generator(t))
            
        self.env.process(self.tick_scheduler())
        
    def task_generator(self, task):
        if task.name == "ASI_MET":
            offset = 0
        elif task.name == "bc_sched":
            offset = 15
        elif task.name.startswith("comm_task"):
            idx = int(task.name.split("_")[-1])
            offset = 17 + (idx * 2) 
        else:
            offset = 0
            
        yield self.env.timeout(offset)
        
        while True:
            job = Job(task.name, task.priority, task.exec_ms, self.env.now + task.deadline_ms)
            self.ready_queue.append(job)
            yield self.env.timeout(task.period_ms)
            
    def apply_pip(self):
        if self.mutex_holder:
            if self.mutex_waiters:
                max_waiter_prio = max(w.eff_priority for w in self.mutex_waiters)
                if max_waiter_prio > self.mutex_holder.base_priority:
                    self.mutex_holder.eff_priority = max_waiter_prio
                    self.inheritance_active_ms += 1
                else:
                    self.mutex_holder.eff_priority = self.mutex_holder.base_priority
            else:
                self.mutex_holder.eff_priority = self.mutex_holder.base_priority

    def tick_scheduler(self):
        while True:
            if self.condition == "baseline":
                if self.mutex_holder:
                    self.mutex_holder.eff_priority = self.mutex_holder.base_priority
            elif self.condition == "pip":
                self.apply_pip()
            elif self.condition == "pcp":
                if self.mutex_holder:
                    self.mutex_holder.eff_priority = self.mutex_ceiling
                    self.inheritance_active_ms += 1  # Record as active whenever raised
                
            runnable_jobs = [j for j in self.ready_queue if not j.wants_mutex or j.holds_mutex or self.mutex_holder is None]
            
            for j in self.ready_queue:
                if j.wants_mutex and not j.holds_mutex and self.mutex_holder is not None and self.mutex_holder != j:
                    # PCP access check: a task can only enter if priority > system ceiling
                    # But if it's the SAME mutex, it simply blocks anyway because it's held!
                    if j.started_waiting_mutex is None:
                        j.started_waiting_mutex = self.env.now
                        if j not in self.mutex_waiters:
                            self.mutex_waiters.append(j)
                            
            if not runnable_jobs:
                yield self.env.timeout(1)
                self.check_deadlines()
                continue
                
            runnable_jobs.sort(key=lambda x: (x.eff_priority, -x.deadline_abs), reverse=True)
            active_job = runnable_jobs[0]
            
            if active_job.wants_mutex and not active_job.holds_mutex and self.mutex_holder is None:
                active_job.holds_mutex = True
                self.mutex_holder = active_job
                if active_job in self.mutex_waiters:
                    self.mutex_waiters.remove(active_job)
                if active_job.started_waiting_mutex is not None:
                    bt = self.env.now - active_job.started_waiting_mutex
                    active_job.blocking_time += bt
                    if active_job.task_name == "bc_sched":
                        self.worst_case_blocking_bc = max(self.worst_case_blocking_bc, bt)
                        self.total_blocking_bc += bt
                        self.bc_jobs_blocked += 1
                    active_job.started_waiting_mutex = None
                    
            active_job.remaining_exec -= 1
            
            task_def = next(t for t in self.spec.tasks if t.name == active_job.task_name)
            executed_so_far = task_def.exec_ms - active_job.remaining_exec
            if active_job.mutex_req_at > 0 and executed_so_far == active_job.mutex_req_at:
                active_job.wants_mutex = True
            
            if active_job.holds_mutex:
                active_job.mutex_duration -= 1
                if active_job.mutex_duration <= 0:
                    active_job.holds_mutex = False
                    active_job.wants_mutex = False
                    self.mutex_holder = None
                    active_job.eff_priority = active_job.base_priority
                    
            if active_job.remaining_exec <= 0:
                self.ready_queue.remove(active_job)
                if active_job.holds_mutex:
                    self.mutex_holder = None
                
            yield self.env.timeout(1)
            self.check_deadlines()
            
    def check_deadlines(self):
        for j in list(self.ready_queue):
            if self.env.now >= j.deadline_abs:
                if j.remaining_exec > 0:
                    self.missed_deadlines += 1
                if j.started_waiting_mutex is not None:
                    bt = self.env.now - j.started_waiting_mutex
                    j.blocking_time += bt
                    if j.task_name == "bc_sched":
                        self.worst_case_blocking_bc = max(self.worst_case_blocking_bc, bt)
                        self.total_blocking_bc += bt
                        self.bc_jobs_blocked += 1
                self.ready_queue.remove(j)
                if j in self.mutex_waiters:
                    self.mutex_waiters.remove(j)
                if self.mutex_holder == j:
                    self.mutex_holder = None

    def run(self):
        self.env.run(until=self.duration)
        mean_blocking = self.total_blocking_bc / max(1, self.bc_jobs_blocked)
        return {
            "worst_case_blocking_bc": float(self.worst_case_blocking_bc),
            "mean_blocking_bc": float(mean_blocking),
            "deadline_misses": self.missed_deadlines,
            "inheritance_active_ms": self.inheritance_active_ms
        }
