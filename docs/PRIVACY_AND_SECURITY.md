# Privacy and security

KubeLore reads only the bundle path passed by the operator. It makes no network
requests while analyzing data and never sends or applies Kubernetes API requests.

Rendered messages redact values following common secret keys (`token`, `password`,
`secret`, `authorization`) and bearer-token patterns. Redaction is defense in depth:
operators should still remove credentials, personal data, and production endpoints
before sharing a bundle or report.

The bundled examples are synthetic and MIT-licensed. They are intentionally local so
tests remain deterministic and no incident data is uploaded.

