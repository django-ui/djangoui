{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ontology-experiment.fullname" -}}
{{- include "common.names.fullname" . -}}
{{- end }}

{{/*
Return the proper image name
*/}}
{{- define "ontology-experiment.image" -}}
{{ include "common.images.image" (dict "imageRoot" .Values.image "global" .Values.global) }}
{{- end -}}

{{/*
Return the proper Docker Image Registry Secret Names
*/}}
{{- define "ontology-experiment.imagePullSecrets" -}}
{{ include "common.images.pullSecrets" (dict "images" (list .Values.image) "global" .Values.global) }}
{{- end -}}

{{/*
Create the name of the Service Account to use
*/}}
{{- define "ontology-experiment.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
    {{- default (include "ontology-experiment.fullname" .) .Values.serviceAccount.name }}
{{- else }}
    {{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Compile all warnings into a single message, and call fail.
*/}}
{{- define "ontology-experiment.validateValues" -}}
{{- $messages := list -}}
{{- $messages := append $messages (include "ontology-experiment.validateValues.extraVolumes" .) -}}
{{- $messages := without $messages "" -}}
{{- $message := join "\n" $messages -}}

{{- if $message -}}
{{-   printf "\nVALUES VALIDATION:\n%s" $message | fail -}}
{{- end -}}
{{- end -}}

{{/* Validate values of - Incorrect extra volume settings */}}
{{- define "ontology-experiment.validateValues.extraVolumes" -}}
{{- if and .Values.extraVolumes (not .Values.extraVolumeMounts) -}}
ontology-experiment: missing-extra-volume-mounts
    You specified extra volumes but not mount points for them.
    Please also set the extraVolumeMounts parameter.
{{- end -}}
{{- end -}}
