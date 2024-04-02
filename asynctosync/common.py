import ast
import time
import inspect
import textwrap
import threading
from functools import partial, wraps

asynciomap = {
    # asyncio function to (additional globals, replacement source) tuples
    "sleep": ({"time": time}, "time.sleep"),
    "Event": ({"threading": threading}, "threading.Event"),
    "create_task": ({"threading": threading}, "threading.Thread"),
}


class AsyncToSync(ast.NodeTransformer):
    def __init__(self):
        self.globals = {}

    def visit_AsyncFunctionDef(self, node):
        return ast.copy_location(
            ast.FunctionDef(
                node.name,
                self.visit(node.args),
                [self.visit(stmt) for stmt in node.body],
                [self.visit(stmt) for stmt in node.decorator_list],
                node.returns and self.visit(node.returns),
            ),
            node,
        )

    def visit_Await(self, node):
        return self.visit(node.value)

    def visit_Attribute(self, node):
        if (
            isinstance(node.value, ast.Name)
            and isinstance(node.value.ctx, ast.Load)
            and node.value.id == "asyncio"
            and node.attr in asynciomap
        ):
            g, replacement = asynciomap[node.attr]
            self.globals.update(g)
            return ast.copy_location(ast.parse(replacement, mode="eval").body, node)
        return node


def _transform_sync_function(f):
    import time

    start_time = time.time()
    filename = inspect.getfile(f)
    lines, lineno = inspect.getsourcelines(f)
    ast_tree = ast.parse(textwrap.dedent("".join(lines)), filename)
    ast.increment_lineno(ast_tree, lineno - 1)

    transformer = AsyncToSync()
    transformer.visit(ast_tree)
    tranformed_globals = {**f.__globals__, **transformer.globals}
    exec(compile(ast_tree, filename, "exec"), tranformed_globals)
    print(time.time() - start_time)
    return tranformed_globals[f.__name__]


def _transform_sync_class(object, f):
    print("transfor call")
    return partial(_transform_sync_function(f), object)


def transform_sync_decorator(func):

    @wraps(func)
    def transform_sync(self, *args, **kwargs):
        test_func = None
        if self.sync and inspect.iscoroutinefunction(
            func
        ):  # Check if it is a coroutine else we will call the decorator again
            test_func = _transform_sync_function(func)
        function_to_call = test_func or func
        return function_to_call(self, *args, **kwargs)

    return transform_sync
