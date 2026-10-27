# Nitro CLI help prototype

Experimental patch and measurements for [nitrojs/nitro#4939](https://github.com/nitrojs/nitro/issues/4939).

The patch keeps command metadata available without loading command implementations for help. Execution imports move into the command paths that need them. It preserves Nitro's original bundle groups. This is a prototype, with duplicated metadata, not a finished contribution.

Base commit: [`5b5bd219397eb50c854eb1240ec844ac5d401b41`](https://github.com/nitrojs/nitro/commit/5b5bd219397eb50c854eb1240ec844ac5d401b41). Node 24.21.0, pnpm 11.28.6, Linux, AMD Ryzen 7 255.

## Results

Medians in milliseconds, 15 fresh Node processes per case and version. One unreported warmup per case, warm filesystem caches, alternating case order. Commands run directly through `node dist/cli/index.mjs`, without a package-manager launcher. Node compile caching was disabled.

| Command | Baseline | Prototype |
| --- | ---: | ---: |
| `--help` | 129.0 | 27.3 |
| `build --help` | 123.0 | 28.0 |
| `dev --help` | 123.4 | 27.0 |
| `--version` | 27.3 | 26.9 |
| Build, 1 route | 230.2 | 230.7 |
| Build, 100 routes | 266.4 | 268.2 |

Help saved about 95–102 ms. Builds showed no measurable improvement. Dev-server readiness was not measured.

The [patch](patches/recommended.patch) adds 103 lines and removes 42 across eight files. [Recorded samples](recorded/final-matrix-samples.json) retain timing, exit status, validation status and system load. CLI output is omitted from this public copy. [Full timing summary](recorded/final-matrix-summary.json).

## Reproduce

Use a fresh clone of this repository and a dedicated Nitro checkout. Install Node 24.21.0, pnpm 11.28.6 and Python 3 first.

```sh
git clone https://github.com/onmax/nitro-cli-startup-lab.git
cd nitro-cli-startup-lab
git clone https://github.com/nitrojs/nitro.git source
git -C source checkout 5b5bd219397eb50c854eb1240ec844ac5d401b41
cd source
pnpm install --frozen-lockfile
git apply --check ../patches/recommended.patch
cd ..
python3 scripts/reproduce.py
```

The script builds the baseline, applies the patch, builds the prototype, creates fixtures and runs the comparison. It modifies only the dedicated `source` checkout and writes new measurements to `results/`. Original measurements remain in `recorded/`. Use a fresh checkout for each full run.

The individual experiments ran in the original lab. The patch passed `git apply --check` against clean source at the pinned commit. The complete clone/install/reproduction recipe above has not been run end to end.

## Validation and limits

The final candidate passed typecheck. Eighteen help, version and error invocations matched baseline output and exit codes. Only `build` ran as a real command. Every generated route returned its expected response through the built fetch handler after timing, without a listening server. Other real commands and the integration suite were not exercised.

The original lab initially borrowed dependencies through a symlink. Its first build reinstalled that directory from the pinned lockfile, affecting another worktree. The lab installation was later isolated and the other worktree restored from its own lockfile. Recorded timings used the resulting pinned dependency set and were not rerun after that repair. The eighteen CLI equivalence checks passed again after isolation. Do not share `node_modules` with another checkout when reproducing.

The scripts are the original lab scripts. They use Linux load averages and are intended for a fresh, single run. Absolute timings vary by machine and cache state.
