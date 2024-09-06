import rpyc
import random
import traceback
from pathlib import Path

import fire

from r2e.paths import TESTGEN_DIR, EXECUTION_DIR
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.execution.execution_args import ExecutionArgs
from r2e.execution.r2e_simulator import DockerSimulator
from r2e.execution.execute_futs import self_equiv_futs
from r2e.models import FunctionUnderTest, MethodUnderTest
from r2e.utils.data import load_functions_under_test, write_functions_under_test


def get_service(repo_id: str, port: int, exp_id: str) -> tuple[DockerSimulator, rpyc.Connection]:
    simulator = DockerSimulator(repo_id=repo_id, 
                                port=port,
                                image_name=f"r2e:{exp_id}")
    try:
        conn = rpyc.connect(
            "localhost", port, keepalive=True, config={"sync_request_timeout": 180}
        )
    except Exception as e:
        print(f"Connection error -- {repo_id} -- {repr(e)}")
        simulator.stop_container()
        raise e
    return simulator, conn


def run_fut_with_port(
    fut: FunctionUnderTest | MethodUnderTest, port: int, args: ExecutionArgs
) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    try:
        simulator, conn = get_service(fut.repo_id, port, args.testgen_exp_id)
    except Exception:
        exception = traceback.format_exc()
        print(f"Service error@{fut.repo_id}:\n{exception}")
        fut.test_history.update_exec_stats({"error": exception})
        return False, exception, fut
    try:
        return self_equiv_futs([fut], conn)
    except Exception:
        tb = traceback.format_exc()
    finally:
        simulator.stop_container()
        conn.close()

    fut.test_history.update_exec_stats({"error": tb})
    print(f"Error@{fut.repo_id}:\n{tb}")
    return False, tb, fut


def run_fut_mp(fut: FunctionUnderTest | MethodUnderTest, args: ExecutionArgs) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:

    # TODO: selected a random port, can collide with other processes!
    port = random.randint(3000, 10000)
    output = run_fut_with_port(fut, port, args)
    return output


def run_self_equiv(exec_args: ExecutionArgs):
    futs = load_functions_under_test(TESTGEN_DIR / f"{exec_args.testgen_exp_id}.json")

    new_futs = []
    if exec_args.execution_multiprocess == 0:
        for fut in futs:
            port = exec_args.port
            try:
                output = run_fut_with_port(fut, port, exec_args)
            except Exception as e:
                print(f"Error@{fut.repo_id}:\n{repr(e)}")
                tb = traceback.format_exc()
                print(tb)
                continue
            new_futs.append(output[2])
    else:

        outputs = run_tasks_in_parallel_iter(
            run_fut_mp,
            [futs, exec_args],
            num_workers=exec_args.execution_multiprocess,
            timeout_per_task=exec_args.timeout_per_task,
            use_progress_bar=True,
        )
        for x in outputs:
            if x.is_success():
                new_futs.append(x.result[2])  # type: ignore
            else:
                print(f"Error: {x.exception_tb}")

    write_functions_under_test(
        new_futs, TESTGEN_DIR / f"{exec_args.testgen_exp_id}_out.json"
    )


if __name__ == "__main__":
    exec_args = fire.Fire(ExecutionArgs)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    run_self_equiv(exec_args)
