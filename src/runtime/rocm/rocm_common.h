/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/*!
 * \file rocm_common.h
 * \brief Common utilities for ROCM
 */
#ifndef TVM_RUNTIME_ROCM_ROCM_COMMON_H_
#define TVM_RUNTIME_ROCM_ROCM_COMMON_H_

#include <hip/hip_runtime_api.h>
#include <hip/hip_version.h>
#include <tvm/ffi/function.h>

#include <string>

#include "../workspace_pool.h"

namespace tvm {
namespace runtime {

#define ROCM_DRIVER_CALL(x)                                                                    \
  {                                                                                            \
    hipError_t result = x;                                                                     \
    if (result != hipSuccess && result != hipErrorDeinitialized) {                             \
      LOG(FATAL) << "ROCM HIP Error: " #x " failed with error: " << hipGetErrorString(result); \
    }                                                                                          \
  }

#define ROCM_CALL(func)                                              \
  {                                                                  \
    hipError_t e = (func);                                           \
    ICHECK(e == hipSuccess) << "ROCM HIP: " << hipGetErrorString(e); \
  }

/*! \brief Thread local workspace */
class ROCMThreadEntry {
 public:
  /*! \brief The hip stream */
  hipStream_t stream{nullptr};
  /*! \brief thread local pool*/
  WorkspacePool pool;
  /*! \brief constructor */
  ROCMThreadEntry();
  // get the threadlocal workspace
  static ROCMThreadEntry* ThreadLocal();
};
}  // namespace runtime
}  // namespace tvm
#endif  // TVM_RUNTIME_ROCM_ROCM_COMMON_H_
