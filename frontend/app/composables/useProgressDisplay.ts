export const getOkrProgressScaleValue = (value: number) => {
  if (value <= 0) {
    return 0
  }

  if (value >= 1) {
    return 1
  }

  if (value >= 0.7) {
    return 0.7
  }

  return 0.3
}

export const formatOkrProgressScaleValue = (value: number) => {
  const normalizedValue = getOkrProgressScaleValue(value)
  return Number.isInteger(normalizedValue) ? String(normalizedValue) : normalizedValue.toFixed(1)
}
