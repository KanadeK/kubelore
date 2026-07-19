# Benchmark

The release process records a deterministic fixture benchmark using Python's
`perf_counter`. The five bundled incidents are deliberately small (4 resources and 2–3
events each); a typical developer laptop should analyze the full set in well under one
second. The observed release value is recorded after the final verification run.

