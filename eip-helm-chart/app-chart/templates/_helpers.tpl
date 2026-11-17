{{/*
Expand the name of the chart.
*/}}
{{- define "app-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "app-chart.fullname" -}}
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
{{- define "app-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "app-chart.labels" -}}
helm.sh/chart: {{ include "app-chart.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if not .Values.global.labels }}
    {{- fail "app, version, component labels are mandatory"  }}
{{- else }}
    {{- with .Values.global.labels -}}
    {{- toYaml . | nindent 0 -}}
    {{- end }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "app-chart.selectorLabels" -}}
app: {{ include "app-chart.name" . }} 
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "app-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "app-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
APM init container Section
*/}}
{{- define "app-chart.apmInitContainer" -}}
- name: elastic-java-agent 
  image: "{{ .Values.apm.image | default "docker.elastic.co/observability/apm-agent-java:1.28.1" }}"
  imagePullPolicy: Always
  volumeMounts: 
  - mountPath: /elastic/apm/agent 
    name: elastic-apm-agent 
  command: ['cp', '-v', '/usr/agent/elastic-apm-agent.jar', '/elastic/apm/agent']
  terminationMessagePath: /dev/termination-log
  terminationMessagePolicy: File
  securityContext:
    runAsNonRoot: false
    readOnlyRootFilesystem: true
  {{- if .Values.apm.resources }}
  resources:
  {{- toYaml .Values.apm.resources | nindent 4 }} 
  {{- end }}
{{- end }}

{{/*
APM volumes Section
*/}}
{{- define "app-chart.apmVolumes" -}}
- name: elastic-apm-agent 
  emptyDir: {}
{{- end }}


{{/*
APM volumeMounts Section
*/}}
{{- define "app-chart.apmVolumeMounts" -}}
- mountPath: /elastic/apm/agent 
  name: elastic-apm-agent
{{- end }}   

{{/*
APPD init container Section
*/}}
{{- define "app-chart.appDInitContainer" -}}
- name: appd-java-agent 
  command:
  - sh
  - -c
  - >-
    cp -r /opt/appdynamics/. /opt/temp &&
    chown -R 1000 /opt/temp
  image: "{{ .Values.appD.image | default "docker.io/appdynamics/java-agent:21.11.4" }}"
  securityContext:
    runAsNonRoot: false  
  {{- if .Values.appD.resources }}
  resources:
  {{- toYaml .Values.appD.resources | nindent 4 }} 
  {{- end }} 
  volumeMounts: 
  - mountPath: /opt/temp
    name: appd-agent-repo
{{- end }}


{{/*
APPD volumes Section
*/}}
{{- define "app-chart.appDVolumes" -}}
- name: appd-agent-repo
  emptyDir: {}
{{- end }}

{{/*
APPD volumeMounts Section
*/}}
{{- define "app-chart.appDVolumeMounts" -}}
- mountPath: /opt/appdynamics
  name: appd-agent-repo
{{- end }}


{{- define "app-chart.annotations" -}}
  {{- if not .Values.global.annotations }}
    {{- fail "owner, cost-center,environment,critical-app annotations are mandatory"  }}
  {{- else }}
    {{- toYaml .Values.global.annotations }}
  {{- end }}
{{- end }}