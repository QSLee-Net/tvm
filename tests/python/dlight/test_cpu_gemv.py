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
# pylint: disable=missing-docstring
import pytest

import tvm.testing
from tvm import dlight as dl
from tvm.script import tir as T
from tvm.target import Target


class BaseBeforeAfter(tvm.testing.CompareBeforeAfter):
    @pytest.fixture
    def transform(self):
        def transform(mod):
            with Target("llvm"):
                return dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)

        return transform


class TestGEMV(BaseBeforeAfter):
    # fmt: off

    @T.prim_func
    def before(lv1637: T.Buffer((1, 32, 1, 128), "float16"), p_lv1638: T.handle, p_lv1614: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": True})
        n = T.int32()
        lv1638 = T.match_buffer(p_lv1638, (1, 32, n, 128), "float16")
        lv1614 = T.match_buffer(p_lv1614, (1, 1, 1, n), "float16")
        var_compute_intermediate = T.match_buffer(p_output0, (1, 32, 1, n))
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((1, 32, 1, n), "float16")
        var_T_divide_intermediate = T.alloc_buffer((1, 32, 1, n), "float16")
        var_T_maximum_intermediate = T.alloc_buffer((1, 32, 1, n), "float16")
        var_T_minimum_intermediate = T.alloc_buffer((1, 32, 1, n), "float16")
        for i0, i1, i2, i3, k in T.grid(1, 32, 1, n, 128):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_i3, v_k = T.axis.remap("SSSSR", [i0, i1, i2, i3, k])
                T.reads(lv1637[v_i0, v_i1, v_i2, v_k], lv1638[v_i0, v_i1, v_i3, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] + lv1637[v_i0, v_i1, v_i2, v_k] * lv1638[v_i0, v_i1, v_i3, v_k]
        for ax0, ax1, ax2, ax3 in T.grid(1, 32, 1, n):
            with T.block("T_divide"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] * T.float16(0.088397790055248615)
        for ax0, ax1, ax2, ax3 in T.grid(1, 32, 1, n):
            with T.block("T_maximum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.max(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], T.float16(-65504))
        for ax0, ax1, ax2, ax3 in T.grid(1, 32, 1, n):
            with T.block("T_minimum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], lv1614[v_ax0, 0, v_ax2, v_ax3])
                T.writes(var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.min(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], lv1614[v_ax0, 0, v_ax2, v_ax3])
        for i0, i1, i2, i3 in T.grid(1, 32, 1, n):
            with T.block("compute"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.writes(var_compute_intermediate[v_i0, v_i1, v_i2, v_i3])
                var_compute_intermediate[v_i0, v_i1, v_i2, v_i3] = T.Cast("float32", var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])

    @T.prim_func
    def expected(lv1637: T.Buffer((1, 32, 1, 128), "float16"), p_lv1638: T.handle, p_lv1614: T.handle, p_output0: T.handle):
        T.func_attr({"tir.is_scheduled": True, "tir.noalias": True})
        n = T.int32()
        lv1638 = T.match_buffer(p_lv1638, (1, 32, n, 128), "float16")
        lv1614 = T.match_buffer(p_lv1614, (1, 1, 1, n), "float16")
        var_compute_intermediate = T.match_buffer(p_output0, (1, 32, 1, n))
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((1, 32, 1, n), "float16")
        for ax0_fused in range(32):
            for ax1_fused_0 in T.parallel((n + 63) // 64):
                for ax1_fused_1 in T.vectorized(64):
                    for ax2_fused_0 in T.serial(2, annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                        for ax2_fused_1, u_0, u_1 in T.grid(64, 1, 1):
                            with T.block("NT_matmul"):
                                v0 = T.axis.spatial(32, ax0_fused)
                                v1 = T.axis.spatial(n, ax1_fused_0 * 64 + ax1_fused_1)
                                v2 = T.axis.reduce(128, ax2_fused_0 * 64 + ax2_fused_1)
                                T.where(ax1_fused_0 * 64 + ax1_fused_1 < n)
                                T.reads(lv1637[0, v0, 0, v2], lv1638[0, v0, v1, v2])
                                T.writes(var_NT_matmul_intermediate[0, v0, 0, v1])
                                with T.init():
                                    var_NT_matmul_intermediate[0, v0, 0, v1] = T.float16(0.0)
                                var_NT_matmul_intermediate[0, v0, 0, v1] = var_NT_matmul_intermediate[0, v0, 0, v1] + lv1637[0, v0, 0, v2] * lv1638[0, v0, v1, v2]
        for ax0, ax1 in T.grid(32, n):
            with T.block("compute"):
                v0, v1 = T.axis.remap("SS", [ax0, ax1])
                T.reads(var_NT_matmul_intermediate[0, v0, 0, v1], lv1614[0, 0, 0, v1])
                T.writes(var_compute_intermediate[0, v0, 0, v1])
                var_compute_intermediate[0, v0, 0, v1] = T.Cast("float32", T.min(T.max(var_NT_matmul_intermediate[0, v0, 0, v1] * T.float16(0.088397790055248615), T.float16(-65504.0)), lv1614[0, 0, 0, v1]))

    # fmt: on


def test_decode_gemv_256_threads():
    # fmt: off
    @T.prim_func(private=True)
    def before(lv571: T.Buffer((22016, 512), "uint32"), lv572: T.Buffer((22016, 128), "float16"), lv1654: T.Buffer((1, 1, 4096), "float16"), var_NT_matmul_intermediate: T.Buffer((1, 1, 22016), "float16")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate = T.alloc_buffer((22016, 4096), "float16")
        for i, j in T.grid(22016, 4096):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv571[v_i, v_j // 8], lv572[v_i, v_j // 32])
                T.writes(p_output0_intermediate[v_i, v_j])
                p_output0_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv571[v_i, v_j // 8], T.Cast("uint32", v_j % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv572[v_i, v_j // 32]
        for i0, i1, i2, k in T.grid(1, 1, 22016, 4096):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv1654[v_i0, v_i1, v_k], p_output0_intermediate[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv1654[v_i0, v_i1, v_k] * p_output0_intermediate[v_i2, v_k]

    @T.prim_func(private=True)
    def expected(lv571: T.Buffer((22016, 512), "uint32"), lv572: T.Buffer((22016, 128), "float16"), lv1654: T.Buffer((1, 1, 4096), "float16"), var_NT_matmul_intermediate: T.Buffer((1, 1, 22016), "float16")):
        T.func_attr({"tir.is_scheduled": True, "tir.noalias": True})
        # with T.block("root"):
        for u_fused in range(1):
            for ax0_fused_0 in T.parallel(172):
                for ax0_fused_1 in T.vectorized(128):
                    for ax1_0_fused_0 in T.serial(8, annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                        for ax1_0_fused_1, ax1_1_0, ax1_1_1 in T.grid(64, 1, 8):
                            with T.block("NT_matmul"):
                                v0 = T.axis.spatial(22016, ax0_fused_0 * 128 + ax0_fused_1)
                                v1 = T.axis.reduce(4096, ax1_0_fused_0 * 512 + ax1_0_fused_1 * 8 + ax1_1_0 * 8 + ax1_1_1)
                                T.reads(lv1654[0, 0, v1], lv571[v0, v1 // 8], lv572[v0, v1 // 32])
                                T.writes(var_NT_matmul_intermediate[0, 0, v0])
                                with T.init():
                                    var_NT_matmul_intermediate[0, 0, v0] = T.float16(0.0)
                                var_NT_matmul_intermediate[0, 0, v0] = var_NT_matmul_intermediate[0, 0, v0] + lv1654[0, 0, v1] * ((T.Cast("float16", T.bitwise_and(T.shift_right(lv571[v0, v1 // 8], T.Cast("uint32", v1 % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv572[v0, v1 // 32])
        # fmt: on

    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], expected)


def test_decode_gemv1():
    # fmt: off

    @T.prim_func(private=True)
    def before(lv571: T.Buffer((22016, 512), "uint32"), lv572: T.Buffer((22016, 128), "float16"), lv1654: T.Buffer((1, 1, 4096), "float16"), var_NT_matmul_intermediate: T.Buffer((1, 1, 22016), "float16")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate = T.alloc_buffer((22016, 4096), "float16")
        for i, j in T.grid(22016, 4096):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv571[v_i, v_j // 8], lv572[v_i, v_j // 32])
                T.writes(p_output0_intermediate[v_i, v_j])
                p_output0_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv571[v_i, v_j // 8], T.Cast("uint32", v_j % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv572[v_i, v_j // 32]
        for i0, i1, i2, k in T.grid(1, 1, 22016, 4096):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv1654[v_i0, v_i1, v_k], p_output0_intermediate[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv1654[v_i0, v_i1, v_k] * p_output0_intermediate[v_i2, v_k]

    @T.prim_func(private=True)
    def expected(lv571: T.Buffer((22016, 512), "uint32"), lv572: T.Buffer((22016, 128), "float16"), lv1654: T.Buffer((1, 1, 4096), "float16"), var_NT_matmul_intermediate: T.Buffer((1, 1, 22016), "float16")):
        T.func_attr({"tir.is_scheduled": True, "tir.noalias": True})
        # with T.block("root"):
        for u_fused in range(1):
            for ax0_fused_0 in T.parallel(172):
                for ax0_fused_1 in T.vectorized(128):
                    for ax1_0_fused_0 in T.serial(8, annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                        for ax1_0_fused_1, ax1_1_0, ax1_1_1 in T.grid(64, 1, 8):
                            with T.block("NT_matmul"):
                                v0 = T.axis.spatial(22016, ax0_fused_0 * 128 + ax0_fused_1)
                                v1 = T.axis.reduce(4096, ax1_0_fused_0 * 512 + ax1_0_fused_1 * 8 + ax1_1_0 * 8 + ax1_1_1)
                                T.reads(lv1654[0, 0, v1], lv571[v0, v1 // 8], lv572[v0, v1 // 32])
                                T.writes(var_NT_matmul_intermediate[0, 0, v0])
                                with T.init():
                                    var_NT_matmul_intermediate[0, 0, v0] = T.float16(0.0)
                                var_NT_matmul_intermediate[0, 0, v0] = var_NT_matmul_intermediate[0, 0, v0] + lv1654[0, 0, v1] * ((T.Cast("float16", T.bitwise_and(T.shift_right(lv571[v0, v1 // 8], T.Cast("uint32", v1 % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv572[v0, v1 // 32])
    # fmt: on

    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], expected)


def test_decode_gemv2():
    # fmt: off

    @T.prim_func(private=True)
    def before(lv771: T.Buffer((32000, 512), "uint32"), lv772: T.Buffer((32000, 128), "float16"), lv3216: T.Buffer((1, 1, 4096), "float16"), p_output0_intermediate: T.Buffer((1, 1, 32000), "float32")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((32000, 4096), "float16")
        var_NT_matmul_intermediate = T.alloc_buffer((1, 1, 32000), "float16")
        for i, j in T.grid(32000, 4096):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv771[v_i, v_j // 8], lv772[v_i, v_j // 32])
                T.writes(p_output0_intermediate_1[v_i, v_j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv771[v_i, v_j // 8], T.Cast("uint32", v_j % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv772[v_i, v_j // 32]
        for i0, i1, i2, k in T.grid(1, 1, 32000, 4096):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv3216[v_i0, v_i1, v_k], p_output0_intermediate_1[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv3216[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_i2, v_k]
        for i0, i1, i2 in T.grid(1, 1, 32000):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(p_output0_intermediate[v_i0, v_i1, v_i2])
                p_output0_intermediate[v_i0, v_i1, v_i2] = T.Cast("float32", var_NT_matmul_intermediate[v_i0, v_i1, v_i2])

    @T.prim_func(private=True)
    def expected(lv771: T.Buffer((32000, 512), "uint32"), lv772: T.Buffer((32000, 128), "float16"), lv3216: T.Buffer((1, 1, 4096), "float16"), p_output0_intermediate: T.Buffer((1, 1, 32000), "float32")):
        T.func_attr({"tir.is_scheduled": True, "tir.noalias": True})
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((1, 1, 32000), "float16")
        for u_fused in range(1):
            for ax0_fused_0 in T.parallel(250):
                for ax0_fused_1 in T.vectorized(128):
                    for ax1_0_fused_0 in T.serial(8, annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                        for ax1_0_fused_1, ax1_1_0, ax1_1_1 in T.grid(64, 1, 8):
                            with T.block("NT_matmul"):
                                v0 = T.axis.spatial(32000, ax0_fused_0 * 128 + ax0_fused_1)
                                v1 = T.axis.reduce(4096, ax1_0_fused_0 * 512 + ax1_0_fused_1 * 8 + ax1_1_0 * 8 + ax1_1_1)
                                T.reads(lv3216[0, 0, v1], lv771[v0, v1 // 8], lv772[v0, v1 // 32])
                                T.writes(var_NT_matmul_intermediate[0, 0, v0])
                                with T.init():
                                    var_NT_matmul_intermediate[0, 0, v0] = T.float16(0.0)
                                var_NT_matmul_intermediate[0, 0, v0] = var_NT_matmul_intermediate[0, 0, v0] + lv3216[0, 0, v1] * ((T.Cast("float16", T.bitwise_and(T.shift_right(lv771[v0, v1 // 8], T.Cast("uint32", v1 % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv772[v0, v1 // 32])
        for ax0 in range(32000):
            with T.block("compute"):
                v0 = T.axis.spatial(32000, ax0)
                T.reads(var_NT_matmul_intermediate[0, 0, v0])
                T.writes(p_output0_intermediate[0, 0, v0])
                p_output0_intermediate[0, 0, v0] = T.Cast("float32", var_NT_matmul_intermediate[0, 0, v0])
    # fmt: on

    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], expected)


def test_decode_gemv3():
    # fmt: off

    @T.prim_func(private=True)
    def before(lv575: T.Buffer((T.int64(4096), T.int64(1376)), "uint32"), lv576: T.Buffer((T.int64(4096), T.int64(344)), "float16"), lv574: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16"), lv570: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((T.int64(4096), T.int64(11008)), "float16")
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(11008)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv575[v_i, v_j // T.int64(8)], lv576[v_i, v_j // T.int64(32)])
                T.writes(p_output0_intermediate_1[v_i, v_j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv575[v_i, v_j // T.int64(8)], T.Cast("uint32", v_j % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv576[v_i, v_j // T.int64(32)]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(4096), T.int64(11008)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv574[v_i0, v_i1, v_k], p_output0_intermediate_1[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv574[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_i2, v_k]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv570[v_ax0, v_ax1, v_ax2], var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv570[v_ax0, v_ax1, v_ax2] + var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func(private=True)
    def expected(lv575: T.Buffer((T.int64(4096), T.int64(1376)), "uint32"), lv576: T.Buffer((T.int64(4096), T.int64(344)), "float16"), lv574: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16"), lv570: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.is_scheduled": True, "tir.noalias": True})
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")
        for u_fused in range(1):
            for ax0_fused_0 in T.parallel(T.int64(64)):
                for ax0_fused_1 in T.vectorized(T.int64(64)):
                    for ax1_0_fused_0 in T.serial(T.int64(11), annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                        for ax1_0_fused_1, ax1_1_0, ax1_1_1 in T.grid(T.int64(128), T.int64(1), T.int64(8)):
                            with T.block("NT_matmul"):
                                v0 = T.axis.spatial(T.int64(4096), ax0_fused_0 * T.int64(64) + ax0_fused_1)
                                v1 = T.axis.reduce(T.int64(11008), (ax1_0_fused_0 * T.int64(128) + ax1_0_fused_1) * T.int64(8) + ax1_1_0 * T.int64(8) + ax1_1_1)
                                T.where(ax1_0_fused_0 * T.int64(128) + ax1_0_fused_1 < T.int64(1376))
                                T.reads(lv574[T.int64(0), T.int64(0), v1], lv575[v0, v1 // T.int64(8)], lv576[v0, v1 // T.int64(32)])
                                T.writes(var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0])
                                with T.init():
                                    var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0] = T.float16(0.0)
                                var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0] = var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0] + lv574[T.int64(0), T.int64(0), v1] * ((T.Cast("float16", T.bitwise_and(T.shift_right(lv575[v0, v1 // T.int64(8)], T.Cast("uint32", v1 % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv576[v0, v1 // T.int64(32)])
        for ax0 in range(T.int64(4096)):
            with T.block("T_add"):
                v0 = T.axis.spatial(T.int64(4096), ax0)
                T.reads(lv570[T.int64(0), T.int64(0), v0], var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0])
                T.writes(p_output0_intermediate[T.int64(0), T.int64(0), v0])
                p_output0_intermediate[T.int64(0), T.int64(0), v0] = lv570[T.int64(0), T.int64(0), v0] + var_NT_matmul_intermediate[T.int64(0), T.int64(0), v0]
    # fmt: on

    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], expected)


def test_autogptq_decode_gemv():
    # fmt: off
    @T.prim_func(private=True)
    def func(lv9: T.Buffer((T.int64(512), T.int64(4096)), "uint32"), lv10: T.Buffer((T.int64(32), T.int64(512)), "uint32"), lv11: T.Buffer((T.int64(32), T.int64(4096)), "float16"), lv12: T.Buffer((T.int64(4096),), "uint32"), lv8: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), lv1613: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(4096)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv9[v_i // T.int64(8), v_j], lv10[lv12[v_i], v_j // T.int64(8)], lv12[v_i], lv11[lv12[v_i], v_j])
                T.writes(decode_intermediate[v_i, v_j])
                decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv9[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8) * T.int64(4))), T.uint32(15))) - (T.Cast("float16", T.bitwise_and(T.shift_right(lv10[lv12[v_i], v_j // T.int64(8)], T.Cast("uint32", v_j % T.int64(8) * T.int64(4))), T.uint32(15))) + T.float16(1))) * lv11[lv12[v_i], v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(4096), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv8[v_i0, v_i1, v_k], decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv8[v_i0, v_i1, v_k] * decode_intermediate[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv1613[v_ax0, v_ax1, v_ax2], var_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv1613[v_ax0, v_ax1, v_ax2] + var_matmul_intermediate[v_ax0, v_ax1, v_ax2]
    # fmt: on

    # The GeMV rule does not yet support the inner dim being grouped.
    # So the rule is expected to skip transforming this function.
    mod = tvm.IRModule({"main": func})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], func)


def test_outer_reduction_adreno():
    # fmt: off
    @T.prim_func(private=True)
    def before(
        lv575: T.Buffer((1376, 4096), "uint32"),
        lv576: T.Buffer((344, 4096), "float16"),
        lv574: T.Buffer((1, 1, 11008), "float16"),
        lv570: T.Buffer((1, 1, 4096), "float16"),
        p_output0_intermediate: T.Buffer((1, 1, 4096), "float16"),
    ):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((11008, 4096), "float16")
        var_matmul_intermediate = T.alloc_buffer((1, 1, 4096), "float16")
        for i, j in T.grid(11008, 4096):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv575[v_i // 8, v_j], T.Cast("uint32", v_i % 8) * T.uint32(4)), T.uint32(15)))- T.float16(7)) * lv576[v_i // 32, v_j]
        for i0, i1, i2, k in T.grid(1, 1, 4096, 11008):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv574[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(1, 1, 4096):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv570[v_ax0, v_ax1, v_ax2] + var_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func(private=True)
    def expected(lv575: T.Buffer((1376, 4096), "uint32"), lv576: T.Buffer((344, 4096), "float16"), lv574: T.Buffer((1, 1, 11008), "float16"), lv570: T.Buffer((1, 1, 4096), "float16"), p_output0_intermediate: T.Buffer((1, 1, 4096), "float16")):
        T.func_attr({"tir.noalias": True})
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((11008, 4096), "float16")
        var_matmul_intermediate = T.alloc_buffer((1, 1, 4096), "float16")
        for i, j in T.grid(11008, 4096):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv575[v_i // 8, v_j], lv576[v_i // 32, v_j])
                T.writes(p_output0_intermediate_1[v_i, v_j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv575[v_i // 8, v_j], T.Cast("uint32", v_i % 8) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv576[v_i // 32, v_j]
        for i0, i1, i2, k in T.grid(1, 1, 4096, 11008):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv574[v_i0, v_i1, v_k], p_output0_intermediate_1[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0.0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv574[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(1, 1, 4096):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv570[v_ax0, v_ax1, v_ax2], var_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv570[v_ax0, v_ax1, v_ax2] + var_matmul_intermediate[v_ax0, v_ax1, v_ax2]
    # fmt: on
    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
    tvm.ir.assert_structural_equal(mod["main"], expected)


def test_outer_reduction_adreno_dynamic():
    # fmt: off
    @T.prim_func(private=True)
    def before(p_lv612: T.handle, p_lv613: T.handle, lv1607: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0: T.handle):
        T.func_attr({"tir.noalias": True})
        v = T.int64()
        lv612 = T.match_buffer(p_lv612, (T.int64(512), v), "uint32")
        lv613 = T.match_buffer(p_lv613, (T.int64(128), v), "float16")
        p_output0_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(1), v))
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((T.int64(4096), v), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), v), "float16")
        for i, j in T.grid(T.int64(4096), v):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv612[v_i // T.int64(8), v_j], lv613[v_i // T.int64(32), v_j])
                T.writes(p_output0_intermediate_1[v_i, v_j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv612[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv613[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), v, T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv1607[v_i0, v_i1, v_k], p_output0_intermediate_1[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv1607[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_k, v_i2]
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), v):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(p_output0_intermediate[v_i0, v_i1, v_i2])
                p_output0_intermediate[v_i0, v_i1, v_i2] = T.Cast("float32", var_matmul_intermediate[v_i0, v_i1, v_i2])

    @T.prim_func(private=True)
    def expected(p_lv612: T.handle, p_lv613: T.handle, lv1607: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0: T.handle):
        T.func_attr({"tir.noalias": True})
        v = T.int64()
        lv612 = T.match_buffer(p_lv612, (T.int64(512), v), "uint32")
        lv613 = T.match_buffer(p_lv613, (T.int64(128), v), "float16")
        p_output0_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(1), v))
        # with T.block("root"):
        p_output0_intermediate_1 = T.alloc_buffer((T.int64(4096), v), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), v), "float16")
        for i, j in T.grid(T.int64(4096), v):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv612[v_i // T.int64(8), v_j], lv613[v_i // T.int64(32), v_j])
                T.writes(p_output0_intermediate_1[v_i, v_j])
                p_output0_intermediate_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv612[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7.0)) * lv613[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), v, T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv1607[v_i0, v_i1, v_k], p_output0_intermediate_1[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0.0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv1607[v_i0, v_i1, v_k] * p_output0_intermediate_1[v_k, v_i2]
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), v):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(p_output0_intermediate[v_i0, v_i1, v_i2])
                p_output0_intermediate[v_i0, v_i1, v_i2] = T.Cast("float32", var_matmul_intermediate[v_i0, v_i1, v_i2])
    # fmt: on

    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
        tvm.ir.assert_structural_equal(mod["main"], expected)


def test_blockized_gemv():
    # fmt: off
    @T.prim_func(private=True)
    def before(x: T.Buffer((1, 4096), "float16"), w: T.Buffer((8, 16384, 4096), "float16"), indptr: T.Buffer((2,), "int32"), o: T.Buffer((2, 16384), "float16")):
        # with T.block("root"):
        for expert_id in T.thread_binding(2, thread="blockIdx.y"):
            with T.block("gemv_o"):
                v_expert_id_o = T.axis.spatial(2, expert_id)
                vi_o = T.axis.spatial(1, 0)
                vj_o = T.axis.reduce(1, 0)
                T.reads(x[0, 0:4096], w[indptr[v_expert_id_o], 0:16384, 0:4096], indptr[v_expert_id_o])
                T.writes(o[v_expert_id_o, 0:16384])
                for i, j in T.grid(16384, 4096):
                    with T.block("gemv"):
                        vi_i, vj_i = T.axis.remap("SR", [i, j])
                        T.reads(x[0, vj_i], w[indptr[v_expert_id_o], vi_i, vj_i], indptr[v_expert_id_o])
                        T.writes(o[v_expert_id_o, vi_i])
                        with T.init():
                            o[v_expert_id_o, vi_i] = T.float16(0)
                        o[v_expert_id_o, vi_i] = o[v_expert_id_o, vi_i] + x[0, vj_i] * w[indptr[v_expert_id_o], vi_i, vj_i]

    @T.prim_func(private=True)
    def expected(x: T.Buffer((1, 4096), "float16"), w: T.Buffer((8, 16384, 4096), "float16"), indptr: T.Buffer((2,), "int32"), o: T.Buffer((2, 16384), "float16")):
        T.func_attr({"tir.is_scheduled": True})
        # with T.block("root"):
        for expert_id in T.thread_binding(2, thread="blockIdx.y"):
            with T.block("gemv_o"):
                v_expert_id_o = T.axis.spatial(2, expert_id)
                vi_o = T.axis.spatial(1, 0)
                vj_o = T.axis.reduce(1, 0)
                T.reads(x[0, 0:4096], w[indptr[v_expert_id_o], 0:16384, 0:4096], indptr[v_expert_id_o])
                T.writes(o[v_expert_id_o, 0:16384])
                for u_fused in range(1):
                    for ax0_fused_0 in T.parallel(128):
                        for ax0_fused_1 in T.vectorized(128):
                            for ax1_fused_0 in T.serial(64, annotations={"pragma_auto_unroll_max_step": 256, "pragma_unroll_explicit": 1}):
                                for ax1_fused_1, u_0, u_1 in T.grid(64, 1, 1):
                                    with T.block("gemv"):
                                        v0 = T.axis.spatial(16384, ax0_fused_0 * 128 + ax0_fused_1)
                                        v1 = T.axis.reduce(4096, ax1_fused_0 * 64 + ax1_fused_1)
                                        T.reads(x[0, v1], w[indptr[v_expert_id_o], v0, v1], indptr[v_expert_id_o])
                                        T.writes(o[v_expert_id_o, v0])
                                        with T.init():
                                            o[v_expert_id_o, v0] = T.float16(0.0)
                                        o[v_expert_id_o, v0] = o[v_expert_id_o, v0] + x[0, v1] * w[indptr[v_expert_id_o], v0, v1]
    # fmt: on
    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
        tvm.ir.assert_structural_equal(mod["main"], expected)


def test_func_to_skip():
    @T.prim_func
    def before(var_A: T.handle, var_exclusive_scan_thrust: T.handle, seq_len: T.int64):
        data_buf = T.match_buffer(var_A, (seq_len * T.int64(8),), "int32", align=8)
        output_buf = T.match_buffer(
            var_exclusive_scan_thrust, (seq_len * T.int64(8),), "int32", align=8
        )
        with T.block("exclusive_scan_thrust"):
            T.reads()
            T.writes()
            T.call_packed(
                "tvm.contrib.thrust.sum_scan",
                T.tvm_stack_make_array(
                    data_buf.data, T.tvm_stack_make_shape(seq_len * T.int64(8)), 0, 1, 0, T.int64(0)
                ),
                T.tvm_stack_make_array(
                    output_buf.data,
                    T.tvm_stack_make_shape(seq_len * T.int64(8)),
                    0,
                    1,
                    0,
                    T.int64(0),
                ),
                T.bool(False),
            )

    # This function should be skipped.
    mod = tvm.IRModule({"main": before})
    with Target("llvm"):
        mod = dl.ApplyDefaultSchedule(dl.cpu.GEMV())(mod)
        tvm.ir.assert_structural_equal(mod["main"], before)


if __name__ == "__main__":
    tvm.testing.main()
