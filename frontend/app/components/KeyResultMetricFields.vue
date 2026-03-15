<script setup lang="ts">
import { getMetricFieldConfig, metricTypeOptions, syncMetricTypeValues } from '~/composables/useOkrForm'

type MetricType = 'number' | 'percent' | 'currency' | 'boolean'

interface MetricFieldForm {
  metricType: MetricType
  startValue: string | number
  currentValue: string | number
  targetValue: string | number
}

const props = withDefaults(defineProps<{
  form: MetricFieldForm
  columnsClass?: string
  labelClass?: string
}>(), {
  columnsClass: 'grid gap-4 md:grid-cols-4',
  labelClass: 'text-sm font-medium text-ink-600',
})
</script>

<template>
  <div :class="columnsClass">
    <div class="space-y-2">
      <label :class="labelClass">Тип метрики</label>
      <select v-model="props.form.metricType" class="input-base" @change="syncMetricTypeValues(props.form)">
        <option v-for="item in metricTypeOptions" :key="item.value" :value="item.value">
          {{ item.label }}
        </option>
      </select>
    </div>

    <div class="space-y-2">
      <label :class="labelClass">Старт</label>
      <select
        v-if="getMetricFieldConfig(props.form.metricType).inputType === 'boolean'"
        v-model="props.form.startValue"
        class="input-base"
      >
        <option value="0">Нет</option>
        <option value="1">Да</option>
      </select>
      <input
        v-else
        v-model="props.form.startValue"
        type="number"
        :step="getMetricFieldConfig(props.form.metricType).step"
        :min="getMetricFieldConfig(props.form.metricType).min"
        :max="getMetricFieldConfig(props.form.metricType).max"
        :placeholder="getMetricFieldConfig(props.form.metricType).placeholders.start"
        class="input-base"
      >
    </div>

    <div class="space-y-2">
      <label :class="labelClass">Текущее</label>
      <select
        v-if="getMetricFieldConfig(props.form.metricType).inputType === 'boolean'"
        v-model="props.form.currentValue"
        class="input-base"
      >
        <option value="0">Нет</option>
        <option value="1">Да</option>
      </select>
      <input
        v-else
        v-model="props.form.currentValue"
        type="number"
        :step="getMetricFieldConfig(props.form.metricType).step"
        :min="getMetricFieldConfig(props.form.metricType).min"
        :max="getMetricFieldConfig(props.form.metricType).max"
        :placeholder="getMetricFieldConfig(props.form.metricType).placeholders.current"
        class="input-base"
      >
    </div>

    <div class="space-y-2">
      <label :class="labelClass">Цель</label>
      <select
        v-if="getMetricFieldConfig(props.form.metricType).inputType === 'boolean'"
        v-model="props.form.targetValue"
        class="input-base"
      >
        <option value="0">Нет</option>
        <option value="1">Да</option>
      </select>
      <input
        v-else
        v-model="props.form.targetValue"
        type="number"
        :step="getMetricFieldConfig(props.form.metricType).step"
        :min="getMetricFieldConfig(props.form.metricType).min"
        :max="getMetricFieldConfig(props.form.metricType).max"
        :placeholder="getMetricFieldConfig(props.form.metricType).placeholders.target"
        class="input-base"
      >
    </div>
  </div>
</template>
