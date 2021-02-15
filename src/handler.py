# -*- coding: utf-8 -*-
# from chalice import Chalice
import os
import sys
import json
import time
from datetime import date, datetime, timedelta
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from loguru import logger
# import numpy

import history_service as service
import validation_json_schemas as schemas

def lambda_handler(request, context):
    """
    This function takes in an arbritary financial function and its parameters as inputs and returns the result of that calculation
    :param request: Dict containing the financial function name (function_name) and its parameters (args)
    :param context: Lambda execution context
    :return: Dict with a 'result' entry containing the result of the calculation
    """
    logger.info("financial function request: {}".format(request))

    try:
        validate(request, schemas.wrapper_schema)
    except ValidationError as err:
        logger.info("Invalid request: {}. Exception: {}".format(request, err))
        return {'error': err.message}

    function_name = request['function_name']
    function_handler_name = function_name + "_function"
    if hasattr(service, function_handler_name):
        return getattr(service, function_handler_name)(request['args'], context)
    else:
        return {"error": "Invalid function name: " + function_name + ". Please see documentation for help on supported functions"}


# def __validate_arguments(function_name, arguments_json, json_schema):
#     """
#     Validate the arguments in the provided JSON against the provided json schema
#     :param function_name:
#     :param arguments_json:
#     :param json_schema:
#     :return: Dict containing whether the provided json is valid and an error message if validation failed.
#     """
#     try:
#         validate(arguments_json, json_schema)
#         return {'isValid': True}
#     except ValidationError as err:
#         logger.error("Invalid {} request with args: {}. Exception: {}".format(function_name, arguments_json, err))
#         return {'isValid': False, 'error': err.message}


# def __call_numpy(method, args):
#     """
#     Call a NumPy method with a given set of arguments
#     :param method: NumPy method to call
#     :param args: Arguments for the provided NumPy method
#     :return: Result from NumPy
#     """
#     logger.info("Calling numpy.{} with args: {}".format(method, args))
#     return {'result': getattr(numpy, method)(*args)}