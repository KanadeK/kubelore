# Benchmark

The release process uses deterministic fixtures. On the release workstation (Windows,
Python 3.12.10), 25 tests including analysis of all five bundles completed in 0.62s.
The five bundled incidents are deliberately small (three Kubernetes resources and one
or two events each); the core analyzer completes their fixture-scale workload well below
one second without network access.
