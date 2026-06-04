# src/xtrllm/df_extractor.py
import warnings
import pandas as pd
from tqdm import tqdm
from ratemate import RateLimit  
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal,Optional

from xtrllm.core.registry import registry
from xtrllm.clients.llm import LLMLibClient
from xtrllm.core.engine import ExtractionEngine
from xtrllm.core.constants import (
    STATUS_SUCCESS,
    STATUS_SKIPPED,
    STATUS_ERROR,
    ON_ERROR_NULL,
    ON_ERROR_RAISE,
)


class DataFrameLLMXtractor:
    def __init__(
        self,
        task: str,
        model: str,
        parameters: dict[str, str] | None = None,
        result_col: str = "result",
        throttler= None,
        on_error: Literal["null", "raise"] = ON_ERROR_NULL,
    ):
        self.task_name = task
        self.task = registry.get(task)()
        self.engine = ExtractionEngine(LLMLibClient(model))
        self.parameters = parameters
        self.result_col = result_col
        self.throttler = throttler
        self.on_error = on_error
        

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_skippable(self, row) -> bool:
        """Return True if this row was already successfully extracted in a prior run."""
        status_col = f"{self.result_col}_status"
        return getattr(row, status_col, None) == STATUS_SUCCESS

    def _kwargs_for_row(self, row) -> dict:
        """Build the keyword arguments to pass to build_prompt / engine.run."""
        if self.parameters:
            return {param: getattr(row, col) for param, col in self.parameters.items()}
        # No explicit mapping — pass every column as a kwarg
        return row._asdict()

    # ------------------------------------------------------------------
    # Public API Sequential
    # ------------------------------------------------------------------

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.parameters:
            for param, col in self.parameters.items():
                if col not in df.columns:
                    raise ValueError(
                        f"Column '{col}' not found in DataFrame (mapped to '{param}')"
                    )

        results = []
        statuses = []

        for i, row in enumerate(tqdm(df.itertuples(index=False), total=len(df), desc="LLMXtractorizing... ")):
            # --- Skip-guard: carry forward successful rows from a prior run ---
            if self.task.skip_if_logged and self._is_skippable(row):
                results.append(getattr(row, self.result_col, None))
                statuses.append(STATUS_SKIPPED)
                continue

            # --- Throttle before hitting the API ---
            if self.throttler:
                self.throttler(i)

            # --- Extract ---
            kwargs = self._kwargs_for_row(row)
            try:
                result = self.engine.run(self.task, **kwargs)
                results.append(result)
                statuses.append(STATUS_SUCCESS)
                if hasattr(self.throttler, "on_success"):
                    self.throttler.on_success() # type: ignore
            except Exception as e:
                if self.on_error == ON_ERROR_RAISE:
                    raise
                warnings.warn(f"Row {i} failed: {e}")
                results.append(None)
                statuses.append(STATUS_ERROR)
                if hasattr(self.throttler, "on_rate_limit"): 
                    self.throttler.on_rate_limit()  # type: ignore

        out = df.copy()
        out[self.result_col] = results
        out[f"{self.result_col}_status"] = statuses
        return out

    # ------------------------------------------------------------------
    # Public API PARALELL
    # ------------------------------------------------------------------
    
    def run_parallel(self, df: pd.DataFrame, rpm=100, max_workers: int = 12) -> pd.DataFrame:
        """Process DataFrame rows in parallel with RPM throttling."""
        
        # Validate input columns
        if self.parameters:
            for param, col in self.parameters.items():
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found in DataFrame (mapped to '{param}')")
        
        # PRE-ALLOCATE result arrays
        results = [None] * len(df)
        statuses: list[Optional[str]] = [None] * len(df)
        
        # THREAD-SAFE RPM throttler (60 seconds window)
        throttler = RateLimit(max_count=rpm, per=60)
        
        def process_row(i, row):
            """Process single row with throttling."""
            try:
                throttler.wait()  # ← Thread-safe RPM enforcement
                kwargs = self._kwargs_for_row(row)
                result = self.engine.run(self.task, **kwargs)
                return result, STATUS_SUCCESS
            except Exception as e:
                if self.on_error == ON_ERROR_RAISE:
                    raise
                warnings.warn(f"Row {i} failed: {e}", stacklevel=2)
                return None, STATUS_ERROR

        # Submit all tasks
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_row, i, row): i
                for i, row in enumerate(df.itertuples(index=False))
            }

            # Collect results as they complete
            for future in tqdm(as_completed(futures), 
                              total=len(df), 
                              desc="LLMXtractorizing..."):
                idx = futures[future]
                try:
                    result, status = future.result()
                    results[idx] = result # type: ignore
                    statuses[idx] = status
                except Exception as e:
                    results[idx] = None
                    statuses[idx] = STATUS_ERROR
                    warnings.warn(f"Future {idx} failed unexpectedly: {e}", stacklevel=2)

        # Build output DataFrame
        out = df.copy()
        out[self.result_col] = results
        out[f"{self.result_col}_status"] = statuses
        return out
    
EXAMPLE = """
# ---------------------------------------------------------------------------
# DataFrameLLMXtractor — Example Usage
# ---------------------------------------------------------------------------

from dotenv import load_dotenv
import os
load_dotenv(r"C:\\LocalSecrets\\master.env")
os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_UIO24EMC_KEY"]

import pandas as pd
from xtrllm import load_tasks
from xtrllm.df_extractor import DataFrameLLMXtractor

# 1. Register tasks from your tasks directory
load_tasks(r"C:\\gitprojects\\pkgs\\xtrllm\\src\\xtrllm\\tasks", namespace="xtrllm")

# 2. Build a DataFrame
df = pd.DataFrame({
    "snippet_text": [
        "The president signed the new trade deal.",
        "Floods devastated the coastal town.",
        "Scientists celebrate breakthrough in cancer research.",
        "Stock markets plunge amid uncertainty.",
        "Local team wins regional championship.",
    ],
    "entities_str": [
        "THE PRESIDENT",
        "THE GOVERNMENT",
        "THE RESEARCH INSTITUTE",
        "THE CENTRAL BANK",
        "THE TEAM",
    ]
})

# 3. Instantiate — map task input param names to DataFrame column names
xtractor = DataFrameLLMXtractor(
    task="uot25rev/sentiment_valence",
    model="gpt-4o-mini",
    parameters={
        "snippet_text": "snippet_text",
        "entities_str": "entities_str",
    },
    result_col="valence",
    on_error="null",
)

# 4. Run 1 — all rows extracted, result_status == STATUS_SUCCESS
df_out = xtractor.run(df)
print(df_out[["snippet_text", "valence", "valence_status"]])

# 5. Run 2 — pass df_out back in; successful rows are skipped automatically
df_out2 = xtractor.run(df_out)
print(df_out2["valence_status"].value_counts())
# valence_status
# SKIPPED    5
# dtype: int64

# 6. Force a full rerun — bump version on the task class, or filter to errors:
df_errors = df_out[df_out["valence_status"] == "ERROR"]
df_rerun = xtractor.run(df_errors)
"""


    # def run_parallel(self, df: pd.DataFrame, max_workers: int = 15) -> pd.DataFrame:
    #     """Parallel execution using thread pool - preserves all existing logic."""
    #     if self.parameters:
    #         for param, col in self.parameters.items():
    #             if col not in df.columns:
    #                 raise ValueError(
    #                     f"Column '{col}' not found in DataFrame (mapped to '{param}')")

    #     lock = Lock()
    #     processed_count = [0]  # mutable counter for throttler

    #     def process_row(i, row):
    #         # --- Skip-guard (thread-safe read) ---
    #         if self.task.skip_if_logged and self._is_skippable(row):
    #             with lock:
    #                 processed_count[0] += 1
    #             return getattr(row, self.result_col, None), STATUS_SKIPPED

    #         # --- CHECK Throttle AdaptiveThrottler ---
    #         if self.throttler is not None:
    #             if not isinstance(self.throttler, AdaptiveThrottler):
    #                 raise TypeError( "Throttler must be an instance of AdaptiveThrottler, "
    #                                 f"got {type(self.throttler).__name__}")
            
    #         # --- Throttle (thread‑safe) ---
    #         if self.throttler:
    #             with lock:
    #                 self.throttler(processed_count[0])
    #                 processed_count[0] += 1

    #         # --- Extract (sync call, but now parallelized) ---
    #         kwargs = self._kwargs_for_row(row)
    #         try:
    #             result = self.engine.run(self.task, **kwargs)
    #             if hasattr(self.throttler, "on_success"):
    #                 self.throttler.on_success() # type: ignore
    #             return result, STATUS_SUCCESS
    #         except Exception as e:
    #             if self.on_error == ON_ERROR_RAISE:
    #                 raise
    #             warnings.warn(f"Row {i} failed: {e}")
    #             if hasattr(self.throttler, "on_rate_limit"):
    #                 self.throttler.on_rate_limit() # type: ignore
    #             return None, STATUS_ERROR

    #     # Execute with thread pool
    #     results  = [None] * len(df)
    #     statuses = [None] * len(df)

    #     with ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         future_to_index = {
    #             executor.submit(process_row, i, row): i
    #             for i, row in enumerate(df.itertuples(index=False))
    #         }

    #         for future in tqdm(as_completed(future_to_index),
    #                            total=len(df),
    #                            desc="Processing rows"):
                
    #             idx = future_to_index[future]
    #             try:
    #                 result, status = future.result()
    #                 results[idx]  = result # type: ignore
    #                 statuses[idx] = status # type: ignore 
    #             except Exception as e:
    #                 results[idx]  = None
    #                 statuses[idx] = STATUS_ERROR # type: ignore
    #                 warnings.warn(f"Future {idx} failed: {e}")

    #     # Build output DataFrame (same as your run() method)
    #     out = df.copy()
    #     out[self.result_col] = results
    #     out[f"{self.result_col}_status"] = statuses
    #     return out