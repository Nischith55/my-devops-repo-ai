{{/*
Expand the name of the chart.
*/}}
{{- define "platform-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "platform-chart.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "platform-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "platform-chart.labels" -}}
helm.sh/chart: {{ include "platform-chart.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "platform-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "platform-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "platform-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "platform-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the minavailable or maxunavailable pods for pdb
*/}}
{{- define "platform-chart.pdbAvailabilitySpec" -}}
{{- if .Values.pdbMinAvailable -}}
minAvailable: {{ .Values.pdbMinAvailable }}
{{- else -}}
maxUnavailable: {{ .Values.pdbMaxUnavailable }}
{{- end }}
{{- end }}

{{/*
virtual service name
*/}}
{{- define "virtual-service.name" -}}
{{- if .Values.virtualService.name }}
{{- .Values.virtualService.name | trunc 63 | trimSuffix "-" }}
{{- else -}}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}


{{/*
destination rule name
*/}}
{{- define "destinationRule.name" -}}
{{- if .Values.destinationRule.name }}
{{- .Values.destinationRule.name | trunc 63 | trimSuffix "-" }}
{{- else -}}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}


