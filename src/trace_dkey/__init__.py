import _ast
import ast
import copy
from typing import Tuple, List, Any, Dict, Union

def __process_tuple(tuple_elts: List) -> Tuple:
    ans = [elt.value for elt in tuple_elts]
    return tuple(ans)

def __trace_key(dict_key: Any, dict_value: Any, key: Any, path: List[Union[str, Tuple]] = []) -> None:
    # path stores the path to the current dict position
    path = copy.deepcopy(path)
    # paths stores all the paths found inside this dict position
    paths = []

    if type(dict_key) == _ast.Constant:
        dict_key_value = dict_key.value
    elif type(dict_key) == _ast.Tuple:
        dict_key_value = __process_tuple(dict_key.elts)
    else:
        return []

    path.append(dict_key_value)
    if dict_key_value == key:
        paths = [path]
    else:
        # branch to iterate over list of keys 
        # this branch will iterate over keys like {'a':1,'b':2,'c':3}
        if (type(dict_value) == _ast.Dict and len(dict_value.keys) > 0):
            for i in range(len(dict_value.keys)):
                # find array of paths inside the ith branch
                branch_paths = __trace_key(dict_value.keys[i], dict_value.values[i], key, path)
                paths = [*paths, *branch_paths]
        
        # branch to iterate over dict of list 
        # this branch will iterate over keys like {'a':1,'b':2,'c':[{'d':'e']}} but skip if c value is list of other types ['d','e']
        if (type(dict_value) == _ast.List):
            for elt in dict_value.elts:
                if type(elt) == _ast.Dict:
                    for i in range(len(elt.keys)):
                        # find array of paths inside the ith branch
                        branch_paths = __trace_key(elt.keys[i], elt.values[i], key, path)
                        paths = [*paths, *branch_paths]
    return paths


def _trace(dictionary: Dict, key: Any) -> List[List]:
    dict_expr = str(dictionary)
    ast_obj = ast.parse(dict_expr, mode="eval")
    paths = []

    for indx in range(len(ast_obj.body.keys)):
        dict_key = ast_obj.body.keys[indx]
        dict_value = ast_obj.body.values[indx]

        trace_res = __trace_key(dict_key, dict_value, key, [])
        paths = [*paths, *trace_res]

    return paths

def trace(dictionary: Dict, key: Any):
    paths = _trace(dictionary,key)

    return paths

