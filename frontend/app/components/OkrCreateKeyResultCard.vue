<script setup lang="ts">
import { Trash2 } from 'lucide-vue-next'
import { okrStatusOptions } from '~/composables/useOkrForm'

type FormStatus = 'draft' | 'on_track' | 'at_risk' | 'completed'
type MetricType = 'number' | 'percent' | 'currency' | 'boolean'

interface KeyResultForm {
  localId: number
  title: string
  description: string
  metricType: MetricType
  startValue: string | number
  currentValue: string | number
  targetValue: string | number
  status: FormStatus
}

const props = defineProps<{
  item: KeyResultForm
  index: number
  canRemove: boolean
}>()

const emit = defineEmits<{
  remove: [localId: number]
}>()

const statusOptions = okrStatusOptions as { value: FormStatus; label: string }[]
</script>

<template>
  <article class="block-radius border border-ink-200 bg-white p-5 shadow-[0_18px_45px_rgba(15,23,42,0.05)]">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <p class="text-xs uppercase tracking-[0.18em] text-ink-400">KR {{ index + 1 }}</p>
        <p class="mt-1 text-sm text-ink-500">Опиши измеримый результат и укажи базовые значения метрики.</p>
      </div>

      <button
        v-if="canRemove"
        type="button"
        class="btn btn-danger btn-sm"
        @click="emit('remove', item.localId)"
      >
        <Trash2 class="h-4 w-4" />
        Удалить
      </button>
    </div>

    <div class="grid gap-4">
      <div class="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
        <input v-model="item.title" type="text" placeholder="Название ключевого результата" class="input-base">
        <select v-model="item.status" class="input-base">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <textarea
        v-model="item.description"
        rows="3"
        class="input-base resize-none"
        placeholder="Описание метрики, ограничения или договорённости по KR."
      />

      <KeyResultMetricFields
        :form="item"
        columns-class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
        label-class="text-xs uppercase tracking-[0.16em] text-ink-400"
      />
    </div>
  </article>
</template>
