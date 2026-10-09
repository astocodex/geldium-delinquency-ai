"""Run the whole analysis in order. Usage: python run_all.py"""
import importlib
import time

STEPS = [("eda", "Data quality checks"), ("modeling", "Model comparison"),
         ("evaluate", "Chosen-model metrics and improvement strategies"),
         ("fairness", "Fairness, proxy and explainability checks"), ("segments", "Segment rates and pilot sizing")]

if __name__ == "__main__":
    for module, label in STEPS:
        print(f"\n===== {label} =====")
        t = time.time()
        importlib.import_module(f"src.{module}").main()
        print(f"[{module} finished in {time.time() - t:.0f}s]")
    print("\nAll outputs saved to the outputs/ folder.")
