class PipelineError(RuntimeError):
    pass

class MissingVariableError(PipelineError):
    pass
