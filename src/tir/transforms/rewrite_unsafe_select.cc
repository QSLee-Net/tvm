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
 * \file unsafe_select_rewrite.cc
 * \brief Rewrite uinsafe select expression.
 */
#include <tvm/ffi/function.h>
#include <tvm/ffi/reflection/registry.h>
#include <tvm/tir/builtin.h>
#include <tvm/tir/expr.h>
#include <tvm/tir/op_attr_types.h>
#include <tvm/tir/stmt_functor.h>
#include <tvm/tir/transform.h>

namespace tvm {
namespace tir {

// For now, rewrite unsafe select expression to if_then_else
// TODO(tqchen) pattern matching to support masked load
class UnsafeExprDetector : public ExprFunctor<bool(const PrimExpr& n)> {
 public:
  // select itself is always considered safe if condition is safe
  // Because we will issue guard to make sure it is.
  bool VisitExpr_(const SelectNode* op) { return VisitExpr(op->condition); }
  bool VisitExpr_(const CallNode* op) {
    if (op->op.same_as(builtin::if_then_else())) {
      return VisitExpr(op->args[0]);
    } else if (op->op.same_as(builtin::address_of())) {
      const BufferLoadNode* load = op->args[0].as<BufferLoadNode>();
      for (const auto& index : load->indices) {
        if (VisitExpr(index)) {
          return true;
        }
      }
      return false;
    } else if (auto opt = op->op.as<Op>()) {
      auto effect_kind = op_call_effect_[opt.value()];
      if (effect_kind == CallEffectKind::kPure || effect_kind == CallEffectKind::kExprAnnotation) {
        for (PrimExpr e : op->args) {
          if (VisitExpr(e)) return true;
        }
        return false;
      } else {
        return true;
      }
    } else {
      return true;
    }
  }
  bool VisitExpr_(const BufferLoadNode* op) {
    // Load is considered unsafe.
    return true;
  }
  bool VisitExpr_(const AddNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const SubNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const MulNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const DivNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const ModNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const FloorDivNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const FloorModNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const MinNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const MaxNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const EQNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const NENode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const LTNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const LENode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const GTNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const GENode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const AndNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const OrNode* op) final { return BinaryOp(op); }
  bool VisitExpr_(const NotNode* op) final { return VisitExpr(op->a); }
  bool VisitExpr_(const LetNode* op) final { return VisitExpr(op->body) || VisitExpr(op->value); }
  bool VisitExpr_(const CastNode* op) final { return VisitExpr(op->value); }
  bool VisitExpr_(const BroadcastNode* op) final { return VisitExpr(op->value); }
  bool VisitExpr_(const RampNode* op) final { return VisitExpr(op->base) && VisitExpr(op->stride); }
  bool VisitExpr_(const ShuffleNode* op) final {
    for (PrimExpr e : op->vectors) {
      if (VisitExpr(e)) return true;
    }
    return false;
  }
  bool VisitExpr_(const VarNode* op) final { return false; }
  bool VisitExpr_(const IntImmNode* op) final { return false; }
  bool VisitExpr_(const FloatImmNode* op) final { return false; }
  bool VisitExpr_(const StringImmNode* op) final { return false; }

 private:
  template <typename T>
  bool BinaryOp(const T* op) {
    return VisitExpr(op->a) || VisitExpr(op->b);
  }

  OpAttrMap<TCallEffectKind> op_call_effect_ = Op::GetAttrMap<TCallEffectKind>("TCallEffectKind");
};

class UnsafeSelectRewriter : public StmtExprMutator {
 public:
  PrimExpr VisitExpr_(const SelectNode* op) {
    PrimExpr expr = StmtExprMutator::VisitExpr_(op);
    op = expr.as<SelectNode>();
    UnsafeExprDetector unsafe;
    bool cond_is_scalar_bool = op->condition.dtype().is_bool() && op->condition.dtype().is_scalar();
    if ((unsafe.VisitExpr(op->true_value) || unsafe.VisitExpr(op->false_value)) &&
        cond_is_scalar_bool) {
      return Call(op->dtype, builtin::if_then_else(),
                  {op->condition, op->true_value, op->false_value});
    } else {
      return expr;
    }
  }
};

Stmt RewriteUnsafeSelect(Stmt stmt) { return UnsafeSelectRewriter()(std::move(stmt)); }

namespace transform {

Pass RewriteUnsafeSelect() {
  auto pass_func = [](PrimFunc f, IRModule m, PassContext ctx) {
    auto* n = f.CopyOnWrite();
    n->body = UnsafeSelectRewriter()(std::move(n->body));
    return f;
  };
  return CreatePrimFuncPass(pass_func, 0, "tir.RewriteUnsafeSelect", {});
}

TVM_FFI_STATIC_INIT_BLOCK({
  namespace refl = tvm::ffi::reflection;
  refl::GlobalDef().def("tir.transform.RewriteUnsafeSelect", RewriteUnsafeSelect);
});

}  // namespace transform

}  // namespace tir
}  // namespace tvm
