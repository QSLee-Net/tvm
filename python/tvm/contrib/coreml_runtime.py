# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""CoreML runtime that load and run coreml models."""
import tvm.ffi
from ..rpc import base as rpc_base


def create(symbol, compiled_model_path, device):
    """Create a runtime executor module given a coreml model and context.
    Parameters
    ----------
    symbol : str
        The symbol that represents the Core ML model.
    compiled_model_path : str
        The path of the compiled model to be deployed.
    device : Device
        The device to deploy the module. It can be local or remote when there
        is only one Device.
    Returns
    -------
    coreml_runtime : CoreMLModule
        Runtime coreml module that can be used to execute the coreml model.
    """
    device_type = device.device_type
    runtime_func = "tvm.coreml_runtime.create"

    if device_type >= rpc_base.RPC_SESS_MASK:
        fcreate = device._rpc_sess.get_function(runtime_func)
    else:
        fcreate = tvm.ffi.get_global_func(runtime_func)
        assert fcreate, "Cannot find `tvm.coreml_runtime.create` function."

    return CoreMLModule(fcreate(symbol, compiled_model_path))


class CoreMLModule(object):
    """Wrapper runtime module.

    This is a thin wrapper of the underlying TVM module.
    you can also directly call set_input, run, and get_output
    of underlying module functions

    Parameters
    ----------
    module : Module
        The internal tvm module that holds the actual coreml functions.

    Attributes
    ----------
    module : Module
        The internal tvm module that holds the actual coreml functions.
    """

    def __init__(self, module):
        self.module = module
        self.invoke = module["invoke"]
        self.set_input = module["set_input"]
        self.get_output = module["get_output"]
        self.get_num_outputs = module["get_num_outputs"]
