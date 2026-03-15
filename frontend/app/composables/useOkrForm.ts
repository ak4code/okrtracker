import type {
  KeyResultCreatePayload,
  KeyResultItem,
  KeyResultUpdatePayload,
  OkrCreatePayload,
  OkrItem,
  OkrUpdatePayload,
} from '~/composables/useOkrApi'

type ApiStatus =
  | OkrCreatePayload['status']
  | OkrUpdatePayload['status']
  | KeyResultCreatePayload['status']
  | KeyResultUpdatePayload['status']

type MetricType =
  | OkrCreatePayload['key_results'][number]['metric_type']
  | KeyResultCreatePayload['metric_type']
  | KeyResultUpdatePayload['metric_type']

interface MetricValuesForm {
  metricType: MetricType
  startValue: string | number
  currentValue: string | number
  targetValue: string | number
}

interface MetricFieldConfig {
  inputType: 'number' | 'boolean'
  step: string
  min?: string
  max?: string
  placeholders: {
    start: string
    current: string
    target: string
  }
}

export const okrStatusOptions: { value: ApiStatus; label: string }[] = [
  { value: 'draft', label: 'Черновик' },
  { value: 'on_track', label: 'В графике' },
  { value: 'at_risk', label: 'Есть риск' },
  { value: 'completed', label: 'Завершён' },
]

export const metricTypeOptions: { value: MetricType; label: string }[] = [
  { value: 'number', label: 'Число' },
  { value: 'percent', label: 'Процент' },
  { value: 'currency', label: 'Деньги' },
  { value: 'boolean', label: 'Да / Нет' },
]

const metricFieldConfig: Record<MetricType, MetricFieldConfig> = {
  number: {
    inputType: 'number',
    step: '0.01',
    placeholders: {
      start: '0',
      current: '0',
      target: 'Например 100',
    },
  },
  percent: {
    inputType: 'number',
    step: '1',
    min: '0',
    max: '100',
    placeholders: {
      start: '0%',
      current: '50%',
      target: '100%',
    },
  },
  currency: {
    inputType: 'number',
    step: '0.01',
    placeholders: {
      start: '0.00',
      current: '50000.00',
      target: '100000.00',
    },
  },
  boolean: {
    inputType: 'boolean',
    step: '1',
    min: '0',
    max: '1',
    placeholders: {
      start: 'Нет',
      current: 'Нет',
      target: 'Да',
    },
  },
}

export const okrStatusToApiMap: Record<OkrItem['status'] | KeyResultItem['status'], ApiStatus> = {
  draft: 'draft',
  'on track': 'on_track',
  'at risk': 'at_risk',
  completed: 'completed',
}

export const normalizeFormValue = (value: string | number) => String(value ?? '').trim()

export const getMetricFieldConfig = (metricType: MetricType) => metricFieldConfig[metricType]

export const normalizeBooleanMetricValue = (value: string | number, fallback: '0' | '1') => {
  const normalized = normalizeFormValue(value).toLowerCase()

  if (['1', 'true', 'yes', 'да'].includes(normalized)) {
    return '1'
  }

  if (['0', 'false', 'no', 'нет'].includes(normalized)) {
    return '0'
  }

  return fallback
}

export const syncMetricTypeValues = (form: MetricValuesForm) => {
  if (form.metricType === 'boolean') {
    form.startValue = normalizeBooleanMetricValue(form.startValue, '0')
    form.currentValue = normalizeBooleanMetricValue(form.currentValue, '0')
    form.targetValue = normalizeBooleanMetricValue(form.targetValue, '1')
    return
  }

  if (!normalizeFormValue(form.startValue)) {
    form.startValue = '0'
  }

  if (!normalizeFormValue(form.currentValue)) {
    form.currentValue = normalizeFormValue(form.startValue) || '0'
  }

  if (form.metricType === 'percent') {
    if (!normalizeFormValue(form.targetValue)) {
      form.targetValue = '100'
    }
    return
  }

  if (form.metricType === 'currency' && !normalizeFormValue(form.targetValue)) {
    form.targetValue = '0.00'
  }
}
