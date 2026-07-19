# KubeLore

KubeLore 将 Kubernetes 导出证据整理为可阅读、可复核的故障链，而不是又一个通用仪表盘。

它离线、只读地分析 Deployment → ReplicaSet → Pod → Container 的关系，并识别镜像拉取、探针、OOM、配置缺失与调度失败五类事故。每条结论都会附带证据、置信度和排查建议。

```bash
python -m pip install -e '.[dev]'
kubelore analyze examples/bundles/image-not-found.json
```

项目不需要集群凭据，不会执行修复操作，也不依赖在线 LLM。使用前请阅读[隐私与安全说明](docs/PRIVACY_AND_SECURITY.md)。完整英文使用指南见 [README.md](README.md)。

