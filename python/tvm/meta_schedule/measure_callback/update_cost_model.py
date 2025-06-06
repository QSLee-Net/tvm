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
"""A measure callback that updates the cost model"""
from tvm.ffi import register_object

from .. import _ffi_api
from .measure_callback import MeasureCallback


@register_object("meta_schedule.UpdateCostModel")
class UpdateCostModel(MeasureCallback):
    def __init__(self) -> None:
        """A measure callback that updates the cost model"""
        self.__init_handle_by_constructor__(
            _ffi_api.MeasureCallbackUpdateCostModel,  # type: ignore # pylint: disable=no-member
        )
