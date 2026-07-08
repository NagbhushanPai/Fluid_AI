class AgentError(Exception):
    pass


class PlanningError(AgentError):
    pass


class ExecutionError(AgentError):
    pass


class BudgetValidationError(AgentError):
    pass

