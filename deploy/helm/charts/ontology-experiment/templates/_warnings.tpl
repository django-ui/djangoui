{{/*
Warning about using rolling tag.
Usage:
{{ include "common.warnings.rollingTag" .Values.path.to.the.imageRoot }}
*/}}
{{- define "common.warnings.rollingTag" -}}

{{- if not (.tag | toString | regexMatch "^.+-\\b[0-9a-f]{8,40}\\b$") }}
WARNING: Rolling tag detected ({{ .repository }}:{{ .tag }}), please note that it is strongly recommended to avoid using rolling tags in a production environment.
{{- end }}

{{- end -}}
