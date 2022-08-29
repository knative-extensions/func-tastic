from parliament import Context
from flask import Request
import numpy as np
from werkzeug.exceptions import MethodNotAllowed, BadRequest, InternalServerError, HTTPException


def numpy_norm_dist(req: Request) -> str:
    if req.method != "POST":
        raise MethodNotAllowed(valid_methods=['POST'])

    if not req.is_json:
        raise BadRequest(description="only JSON body allowed")

    try:
        request_data = req.get_json()
        v1 = np.fromstring(request_data["v1"], dtype=int, sep=' ')
        v2 = np.fromstring(request_data["v2"], dtype=int, sep=' ')
    except KeyError:
        raise BadRequest(description='missing v1 or v2 in body')
    except Exception as e:
        raise InternalServerError(original_exception=e)

    if v1.size != v2.size:
        raise BadRequest(description='v1 and v2 have different size')

    return str(np.linalg.norm(v1 - v2))


# Accept json
# Input sample: {"v1":"3 4 5 6","v2":"3 4 5 6"}


def main(context: Context):
    """
    Calculate the Euclidean distance using NumPy
    """
    print("Received request")

    if 'request' in context.keys():
        try:
            ret = numpy_norm_dist(context.request)
            print(ret, flush=True)
            return ret, 200
        except HTTPException as e:
            return e
    else:
        print("Empty request", flush=True)
        return "{}", 200
