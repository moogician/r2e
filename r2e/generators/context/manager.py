from r2e.models.function import Function
from r2e.models.method import Method
from r2e.models.context import Context
from r2e.common.cache import ContextCache
from r2e.generators.context import (
    ContextCreator,
    FullContextCreator,
    SlicedContextCreator,
)


class ContextManager:

    @staticmethod
    def get_context(
        context_type: str, func_meth: Function | Method, max_context_size: int
    ) -> Context:
        context = ContextCache[(func_meth.repo.repo_id, func_meth.id, context_type)]
        if context is not None:
            return context

        if context_type == "naive":
            nc = ContextCreator(func_meth, max_context_size)
            nc.construct_context()
            context = nc.get_context()

        elif context_type == "full":
            context = FullContextCreator(func_meth, max_context_size).get_context()

        elif context_type == "sliced":
            context = SlicedContextCreator(func_meth, max_context_size).get_context()

        else:
            raise ValueError(f"Invalid context type: {context_type}")
        
        ContextCache[(func_meth.repo.repo_id, func_meth.id, context_type)] = context
        return context
