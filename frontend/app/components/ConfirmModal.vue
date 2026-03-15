<script setup lang="ts">
import { AlertTriangle, X } from 'lucide-vue-next'

withDefaults(defineProps<{
  modelValue: boolean
  title?: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  isLoading?: boolean
}>(), {
  title: 'Подтвердить действие',
  description: '',
  confirmLabel: 'Подтвердить',
  cancelLabel: 'Отмена',
  isLoading: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
}>()

const closeModal = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[70] flex items-center justify-center bg-ink-900/45 px-4 py-8 backdrop-blur-sm"
      @click.self="closeModal"
    >
      <div class="surface w-full max-w-md p-6 shadow-2xl sm:p-7">
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="rounded-2xl bg-amber-100 p-2 text-amber-500">
              <AlertTriangle class="h-5 w-5" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-ink-900">{{ title }}</h2>
              <p v-if="description" class="mt-2 text-sm leading-6 text-ink-600">{{ description }}</p>
            </div>
          </div>

          <button class="btn btn-secondary btn-icon" aria-label="Закрыть модалку" @click="closeModal">
            <X class="h-4 w-4" />
          </button>
        </div>

        <div class="mt-6 flex flex-wrap items-center justify-end gap-3">
          <button type="button" class="btn btn-secondary" :disabled="isLoading" @click="closeModal">
            {{ cancelLabel }}
          </button>
          <button type="button" class="btn btn-danger" :disabled="isLoading" @click="emit('confirm')">
            {{ isLoading ? 'Выполняем...' : confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
