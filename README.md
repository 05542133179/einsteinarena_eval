# OpenArena Eval Kit

这是一个从现有评测工程中拆出的、可以独立运行的 EinsteinArena/OpenArena
评测包。它只保留四件事：

1. 自动拉取当前 construction problems 和官方 Python verifier；
2. 固化题目、verifier 源码及 SHA-256，支持离线校验；
3. 用同一份 verifier 在本地复现单题或批量打分；
4. 自动拉取各题公开榜单，并可把本地结果插入为虚拟排名。

包内已经附带 17 道题的冻结快照。评分不依赖原工程、模型服务、GPU、rjob
或 API key。

## 快速开始

要求 Python 3.10+。建议使用 Linux；官方 verifier 依赖 NumPy、SciPy 和
mpmath。

```bash
git clone https://github.com/05542133179/einsteinarena_eval.git
cd einsteinarena_eval

python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .

scripts/smoke_test.sh
```

也可以不安装命令行入口，直接在仓库根目录运行：

```bash
python3 -m openarena_eval validate
```

## 1. 查看和校验题目

列出当前打包题目：

```bash
openarena-eval list
```

查看一道题的描述、评分方向和 candidate schema：

```bash
openarena-eval show --slug difference-bases
```

校验题目列表、冻结 API 响应、本地 verifier 和所有哈希：

```bash
openarena-eval validate
```

成功时输出中的 `valid` 为 `true`。任何 verifier 被意外修改都会导致校验失败。

## 2. 本地复现单题打分

候选文件只放官方 verifier 接收的 JSON 对象，不要再包一层
`candidate`：

```bash
openarena-eval score \
  --slug difference-bases \
  --candidate examples/difference-bases.json
```

该例会得到有限的官方原始分数 `4.0`。结果中的主要字段：

| 字段 | 含义 |
|---|---|
| `valid` | candidate 是否通过格式检查并得到有限 verifier 分数 |
| `raw_score` | 官方 verifier 原始分数 |
| `scoring` | `maximize` 或 `minimize` |
| `directional_score` | 统一成越大越好；minimize 题取 `-raw_score` |
| `reason` | `ok` 或具体失败原因 |
| `snapshot_id` | 本次使用的冻结 verifier 快照 |
| `verifier_sha256` | 该题 verifier 的精确哈希 |

读取标准输入：

```bash
printf '%s\n' '{"set":[0,1]}' | \
  openarena-eval score --slug difference-bases --candidate -
```

如果输入是完整模型回答，回答末尾必须是：

```text
FINAL_CANDIDATE_JSON:
{"set":[0,1]}
```

然后运行：

```bash
openarena-eval score \
  --slug difference-bases \
  --model-output path/to/model_output.txt
```

解析器只接受最后一个 marker 后面的单个严格 JSON 对象；尾随文字、NaN、
Infinity 和错误 Markdown fence 都会被拒绝。

## 3. 批量评分

输入 JSONL 每行支持两种格式：

```json
{"slug":"difference-bases","candidate_id":"run-1","candidate":{"set":[0,1]}}
{"slug":"difference-bases","candidate_id":"run-2","model_output":"FINAL_CANDIDATE_JSON:\n{\"set\":[0,1]}"}
```

执行：

```bash
mkdir -p results

openarena-eval batch \
  --input examples/candidates.jsonl \
  --output results/scores.jsonl
```

生成：

```text
results/
├── scores.jsonl
└── scores.summary.json
```

summary 会按题选择 best-of-k，并报告 candidate 合法率和 valid@k。不同题目的
`raw_score` 不应直接求平均。

## 4. 在线刷新题目和 verifier

```bash
scripts/refresh_tasks.sh
```

刷新过程会：

1. 请求 `GET /api/problems`；
2. 保留已有题目顺序并追加新 construction problem；
3. 请求 `GET /api/problems/<slug>`；
4. 校验每份 verifier 都定义了 `evaluate(data)`；
5. 重建 `data/openarena.jsonl`、每题目录和全部哈希。

默认拒绝静默删题。确认官网变化后才使用：

```bash
scripts/refresh_tasks.sh --allow-removals
```

临时排除或重新纳入题目：

```bash
scripts/refresh_tasks.sh --exclude-slug <slug>
scripts/refresh_tasks.sh --include-slug <slug>
```

如果运行环境需要代理，使用标准环境变量，不需要修改脚本：

```bash
export HTTPS_PROXY=http://proxy.example:3128
export HTTP_PROXY="$HTTPS_PROXY"
scripts/refresh_tasks.sh
```

刷新属于显式更新快照的操作。提交仓库前应检查：

```bash
git diff -- data/
openarena-eval validate
```

## 5. 拉取公开榜单

只拉取官方榜单：

```bash
scripts/pull_leaderboard.sh --top-k 10
```

把批量本地评分一并插入：

```bash
scripts/pull_leaderboard.sh \
  --top-k 10 \
  --local-results results/scores.jsonl \
  --local-label my-agent
```

每次运行写入独立时间戳目录：

```text
outputs/YYYY-MM-DD_HHMMSS/
├── overview.csv       # 每题第一名及本地 best/虚拟排名
├── leaderboard.csv    # 每题 Top-K 长表及本地结果
├── leaderboard.xlsx   # 两个带样式 sheet
└── raw.json           # 本次原始 API 响应与 URL
```

本地虚拟排名按当前官方分数插入；同分时排在已有官方同分条目之后。它不是官网
正式排名，也不会向官网提交 candidate。

## 目录

```text
openarena-eval-kit/
├── data/
│   ├── manifest.json
│   ├── openarena.jsonl
│   ├── official_snapshot/
│   └── problems/<slug>/
├── examples/
├── openarena_eval/
│   ├── cli.py
│   ├── evaluator.py
│   ├── verifier_worker.py
│   ├── sync.py
│   └── leaderboard.py
├── scripts/
├── tests/
├── pyproject.toml
└── README.md
```

## 可复现性和安全边界

- 每次评分都使用 `data/problems/<slug>/code/verifier.py`，并可通过冻结 API
  响应的 SHA-256 反查。
- verifier 在独立子进程中运行；默认 wall time 120 秒、内存上限 8 GiB、
  candidate JSON 最大 32 MiB。
- 上游 verifier 是可执行 Python。只应从可信的 EinsteinArena 官方 API
  刷新，并先在隔离环境中审查变更。
- Unix 会设置 CPU/地址空间限制；不提供 `resource` 模块的平台只能依赖父进程
  wall-time 超时。
- 当前 17 题包含网站输入形状的本地预检查。自动发现全新题目后，官方 Python
  verifier 仍会运行，但若官网另有 verifier 之外的输入约束，应同步补充本地
  shape 检查并加入测试。

## 测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖快照哈希、已知候选分数、严格模型输出解析、离线题目刷新和离线榜单
导出。`scripts/smoke_test.sh` 会同时执行 CLI 校验、真实 verifier 打分和完整
测试。

## 上游与许可

- 官网与公开榜单：<https://einsteinarena.com/>
- 上游源码：<https://github.com/vinid/einstein-arena>
- 随包题目/verifier 的上游许可见
  `data/LICENSE.einstein-arena` 和 `THIRD_PARTY_NOTICES.md`。

本地工具代码目前未主动指定开源许可证。正式建立公开 GitHub 仓库前，应由仓库
所有者选择并加入 `LICENSE`。
