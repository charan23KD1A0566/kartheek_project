#!/usr/bin/env python3
"""Wrapper to run the test and save output to a file"""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "d:\\sif sentimental\\backend\\run_10_case_sanity_test.py"],
    cwd="d:\\sif sentimental\\backend",
    capture_output=True,
    text=True
)

# Write output to file
with open("d:\\sif sentimental\\test_output.txt", "w") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n\nSTDERR:\n")
        f.write(result.stderr)

print("Test complete. Output written to d:\\sif sentimental\\test_output.txt")
print(f"Return code: {result.returncode}")
