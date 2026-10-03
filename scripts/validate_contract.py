#!/usr/bin/env python3
"""Validate Scale execution-contract structure and status consistency."""

import argparse
import json
import sys

STATES={"RUNNING","COMPLETE","BLOCKED","REPLAN_REQUIRED","APPROVAL_REQUIRED","BUDGET_EXHAUSTED","FAIL_CLOSED"}
GATES={"PASS","FAIL","UNCERTAIN","NOT_RUN"}
EFFORTS={"none","low","medium","high","xhigh","max"}

def validate(c, baseline=None):
    errors=[]
    def need(ok,msg):
        if not ok:
            errors.append(msg)

    if not isinstance(c,dict):
        return ["contract must be an object"]

    need(c.get("schema_version")=="1.0","schema_version must be 1.0")
    for k in ("contract_id","goal","deliverable"):
        need(isinstance(c.get(k),str) and bool(c[k].strip()),f"{k} must be nonempty")
    need(type(c.get("revision")) is int and c["revision"]>0,"revision must be a positive integer")
    need(c.get("status") in STATES,"invalid status")

    collections={}
    for key in ("protected_constraints","gates","dependencies","effects","required_outputs"):
        value=c.get(key)
        if not isinstance(value,list):
            errors.append(f"{key} must be a list")
            value=[]
        collections[key]=value
        ids=[]
        for row in value:
            if not isinstance(row,dict):
                errors.append(f"{key} entries must be objects")
                continue
            ident=row.get("id")
            need(isinstance(ident,str) and bool(ident.strip()),f"{key} entry needs id")
            if isinstance(ident,str):
                ids.append(ident)
        need(len(ids)==len(set(ids)),f"duplicate id in {key}")

    for p in collections["protected_constraints"]:
        if isinstance(p,dict):
            for k in ("value","source"):
                need(isinstance(p.get(k),str) and bool(p[k].strip()),f"constraint {p.get('id')} needs {k}")

    required_gates=[]
    for g in collections["gates"]:
        if not isinstance(g,dict):
            continue
        need(type(g.get("required")) is bool,"gate required must be boolean")
        if g.get("required") is True:
            required_gates.append(g)
        need(g.get("status") in GATES,f"gate {g.get('id')} invalid status")
        for k in ("property","verifier"):
            need(isinstance(g.get(k),str) and bool(g[k].strip()),f"gate {g.get('id')} needs {k}")
        if g.get("status")=="PASS":
            need(isinstance(g.get("evidence"),str) and bool(g["evidence"].strip()),f"PASS gate {g.get('id')} needs evidence")
    need(bool(required_gates),"at least one required gate is needed")

    allowed_status={
        "dependencies":{"READY","BLOCKED","UNKNOWN"},
        "effects":{"SUCCESS","FAILED","UNKNOWN_EFFECT","NOT_RUN"},
        "required_outputs":{"PRESENT","MISSING","UNKNOWN"},
    }
    for kind in ("dependencies","effects","required_outputs"):
        for row in collections[kind]:
            if not isinstance(row,dict):
                continue
            if kind!="required_outputs":
                need(type(row.get("required")) is bool,f"{kind} required must be boolean")
            need(row.get("status") in allowed_status[kind],f"{kind} {row.get('id')} invalid status")
            if kind=="dependencies":
                need("expected_version" in row,f"dependency {row.get('id')} needs expected_version")
                need("observed_version" in row,f"dependency {row.get('id')} needs observed_version")

    route=c.get("route")
    if not isinstance(route,dict):
        errors.append("route must be an object")
    else:
        for k in ("requested_model","observed_model","identity_source","surface","actuation"):
            need(k in route,f"route needs {k}")
        allowed=route.get("allowed_efforts")
        need(isinstance(allowed,list) and bool(allowed) and all(v in EFFORTS for v in allowed),"invalid allowed_efforts")
        if isinstance(allowed,list):
            need(route.get("effort") in allowed,"effort outside allowed_efforts")
        need(route.get("actuation") in {"RECOMMENDATION","APPLIED","CURRENT_UNCHANGED"},"invalid route actuation")
        if route.get("actuation")=="APPLIED":
            need(bool(route.get("actuation_evidence")),"APPLIED route needs actuation evidence")

    budget=c.get("budget")
    need(isinstance(budget,dict),"budget must be an object")
    if isinstance(budget,dict):
        need(type(budget.get("exhausted")) is bool,"budget.exhausted must be boolean")
        if c.get("status")=="BUDGET_EXHAUSTED":
            need(budget.get("exhausted") is True and bool(budget.get("evidence")),"BUDGET_EXHAUSTED needs observed limit evidence")

    if c.get("status")=="COMPLETE":
        need(all(g.get("status")=="PASS" for g in required_gates),"COMPLETE has unresolved required gate")
        need(bool(collections["required_outputs"]),"COMPLETE needs a required output")
        need(all(isinstance(o,dict) and o.get("status")=="PRESENT" and bool(o.get("evidence")) for o in collections["required_outputs"]),"COMPLETE needs present evidenced outputs")
        for d in collections["dependencies"]:
            if isinstance(d,dict) and d.get("required") is True:
                need(d.get("status")=="READY",f"COMPLETE has blocked dependency {d.get('id')}")
                need(d.get("expected_version") is not None and d.get("observed_version")==d.get("expected_version"),f"COMPLETE has stale/unknown dependency {d.get('id')}")
        for e in collections["effects"]:
            if isinstance(e,dict) and e.get("required") is True:
                need(e.get("status")=="SUCCESS" and bool(e.get("evidence")),f"COMPLETE has unresolved effect {e.get('id')}")

    if baseline is not None:
        need(isinstance(baseline,dict),"baseline must be an object")
        if isinstance(baseline,dict):
            for k in ("contract_id","goal","deliverable","protected_constraints"):
                need(c.get(k)==baseline.get(k),f"protected baseline changed: {k}")
            def required(x):
                return [{k:g.get(k) for k in ("id","property","verifier","required")}
                        for g in x.get("gates",[]) if isinstance(g,dict) and g.get("required") is True]
            need(required(c)==required(baseline),"required gate definitions changed")

    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("contract")
    p.add_argument("--baseline")
    args=p.parse_args()
    try:
        with open(args.contract,encoding="utf-8") as fh:
            contract=json.load(fh)
        baseline=None
        if args.baseline:
            with open(args.baseline,encoding="utf-8") as fh:
                baseline=json.load(fh)
        errors=validate(contract,baseline)
    except (OSError,ValueError,TypeError) as exc:
        errors=[str(exc)]
    print(json.dumps({"valid":not errors,"errors":errors,"scope":"structure_and_status_only"},ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=="__main__":
    raise SystemExit(main())
