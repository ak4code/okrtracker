import type { KeyResultItem } from '~/composables/useOkrApi'

export const formatMetricValue = (value: number, unit: string) => {
  if (unit === '%') {
    return `${value}${unit}`
  }

  if (unit === 'bool') {
    return value ? 'Да' : 'Нет'
  }

  return `${value} ${unit}`.trim()
}

export const formatKeyResultValue = (value: number) => {
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}

export const formatPercentProgress = (value: number) => `${Math.round(value * 100)}%`

export const getCommentInitials = (author: string) => {
  const parts = author.trim().split(/\s+/).filter(Boolean)

  if (!parts.length) {
    return 'OK'
  }

  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || '')
    .join('')
}

export const getKeyResultScaleClass = (value: number) => {
  if (value >= 1) {
    return 'border-mint-500/20 bg-mint-100/60'
  }

  if (value >= 0.7) {
    return 'border-amber-200 bg-amber-100/60'
  }

  if (value >= 0.3) {
    return 'border-sky-200 bg-sky-100/60'
  }

  return 'border-ink-200 bg-ink-100/70'
}

export const getKeyResultScaleBadgeClass = (value: number) => {
  if (value >= 1) {
    return 'border-mint-500/20 bg-mint-100 text-mint-500'
  }

  if (value >= 0.7) {
    return 'border-amber-200 bg-amber-100 text-amber-600'
  }

  if (value >= 0.3) {
    return 'border-sky-200 bg-sky-100 text-sky-600'
  }

  return 'border-ink-200 bg-ink-100 text-ink-600'
}

export const isKeyResultCompleted = (keyResult: KeyResultItem) => keyResult.progress >= 1 || keyResult.status === 'completed'
