<script setup lang="ts">
definePageMeta({
  title: 'Настройки',
})

import { Pencil, Plus, Save, X } from 'lucide-vue-next'

type SettingsSection = 'quarters' | 'roles' | 'users' | 'teams' | 'notifications'

interface QuarterFormState {
  year: number
  quarter: number
  startDate: string
  endDate: string
  isActive: boolean
}

interface EditableQuarterState extends QuarterFormState {
  id?: number | null
  startDateRaw?: string
  endDateRaw?: string
}

interface TeamFormState {
  name: string
  code: string
  description: string
}

interface RoleFormState {
  name: string
  code: string
  description: string
}

interface UserFormState {
  email: string
  firstName: string
  lastName: string
  roleId: number | null
  primaryTeamId: number | null
  teamIds: number[]
  isActive: boolean
  isStaff: boolean
  password: string
}

const okrApi = useOkrApi()
const coreApi = useCoreApi()
const dashboardQuarter = useState<string>('dashboard-quarter', () => '')
const activeSection = ref<SettingsSection>('quarters')

const isQuarterModalOpen = ref(false)
const isRoleModalOpen = ref(false)
const isTeamModalOpen = ref(false)
const isUserModalOpen = ref(false)

const editingQuarterId = ref<number | null>(null)
const editingRoleId = ref<number | null>(null)
const editingTeamId = ref<number | null>(null)
const editingUserId = ref<number | null>(null)

const quarterModalKey = ref(0)
const roleModalKey = ref(0)
const teamModalKey = ref(0)
const userModalKey = ref(0)

const createDefaultQuarterForm = (): QuarterFormState => ({
  year: new Date().getFullYear(),
  quarter: 1,
  startDate: '',
  endDate: '',
  isActive: false,
})

const quarterForm = ref<QuarterFormState>(createDefaultQuarterForm())
const roleForm = ref<RoleFormState>({ name: '', code: '', description: '' })
const teamForm = ref<TeamFormState>({ name: '', code: '', description: '' })
const userForm = ref<UserFormState>({
  email: '',
  firstName: '',
  lastName: '',
  roleId: null,
  primaryTeamId: null,
  teamIds: [],
  isActive: true,
  isStaff: false,
  password: '',
})

const sections: { id: SettingsSection, label: string }[] = [
  { id: 'quarters', label: 'Кварталы' },
  { id: 'roles', label: 'Роли' },
  { id: 'users', label: 'Пользователи' },
  { id: 'teams', label: 'Команды' },
  { id: 'notifications', label: 'Уведомления' },
]

const quarterErrorMessage = ref('')
const quarterSuccessMessage = ref('')
const isQuarterSubmitting = ref(false)

const teamErrorMessage = ref('')
const teamSuccessMessage = ref('')
const isTeamSubmitting = ref(false)

const roleErrorMessage = ref('')
const roleSuccessMessage = ref('')
const isRoleSubmitting = ref(false)

const userErrorMessage = ref('')
const userSuccessMessage = ref('')
const isUserSubmitting = ref(false)

const { data: quarterOptions, pending: quartersPending, refresh: refreshQuarters } = await useAsyncData(
  'okr-quarters',
  () => okrApi.fetchQuarters(),
  { server: false, default: () => [] },
)

const { data: rolesOptions } = await useAsyncData(
  'core-roles',
  () => coreApi.fetchRoles(),
  { server: false, default: () => [] },
)

const { data: teamsOptions, pending: teamsPending, refresh: refreshTeams } = await useAsyncData(
  'core-teams',
  () => coreApi.fetchTeams(),
  { server: false, default: () => [] },
)

const { data: usersOptions, pending: usersPending, refresh: refreshUsers } = await useAsyncData(
  'core-users',
  () => coreApi.fetchUsers(),
  { server: false, default: () => [] },
)

const isQuarterSection = computed(() => activeSection.value === 'quarters')

const quarterFormTitle = computed(() => (editingQuarterId.value ? 'Редактировать квартал' : 'Создать квартал'))
const quarterFormButtonLabel = computed(() => (editingQuarterId.value ? 'Сохранить изменения' : 'Добавить квартал'))

const resetQuarterMessages = () => {
  quarterErrorMessage.value = ''
  quarterSuccessMessage.value = ''
}

const fillQuarterForm = (payload?: EditableQuarterState) => {
  editingQuarterId.value = payload?.id ?? null
  quarterForm.value = {
    year: payload?.year ?? new Date().getFullYear(),
    quarter: payload?.quarter ?? 1,
    startDate: payload?.startDateRaw ?? '',
    endDate: payload?.endDateRaw ?? '',
    isActive: payload?.isActive ?? false,
  }
}

const closeQuarterModal = () => {
  isQuarterModalOpen.value = false
  fillQuarterForm()
  resetQuarterMessages()
}

const openCreateQuarterModal = () => {
  fillQuarterForm()
  resetQuarterMessages()
  quarterModalKey.value += 1
  nextTick(() => {
    isQuarterModalOpen.value = true
  })
}

const startEditingQuarter = (quarter: EditableQuarterState) => {
  activeSection.value = 'quarters'
  fillQuarterForm(quarter)
  resetQuarterMessages()
  quarterModalKey.value += 1
  nextTick(() => {
    isQuarterModalOpen.value = true
  })
}

const submitQuarter = async () => {
  isQuarterSubmitting.value = true
  resetQuarterMessages()

  try {
    const payload = {
      year: quarterForm.value.year,
      quarter: quarterForm.value.quarter,
      start_date: quarterForm.value.startDate,
      end_date: quarterForm.value.endDate,
      is_active: quarterForm.value.isActive,
    }

    const quarter = editingQuarterId.value
      ? await okrApi.updateQuarter(editingQuarterId.value, payload)
      : await okrApi.createQuarter(payload)

    await refreshQuarters()
    await refreshNuxtData('okr-quarters')

    if (quarter.isActive) {
      dashboardQuarter.value = quarter.name
    }

    quarterSuccessMessage.value = editingQuarterId.value
      ? `Квартал ${quarter.name} обновлён.`
      : `Квартал ${quarter.name} создан.`

    isQuarterModalOpen.value = false
    fillQuarterForm()
  }
  catch (error: any) {
    const apiError = error?.data || error?.response?._data
    if (apiError && typeof apiError === 'object') {
      const firstMessage = Object.values(apiError).flat().find(Boolean)
      quarterErrorMessage.value = String(firstMessage)
    }
    else {
      quarterErrorMessage.value = editingQuarterId.value
        ? 'Не удалось обновить квартал.'
        : 'Не удалось создать квартал.'
    }
  }
  finally {
    isQuarterSubmitting.value = false
  }
}

const resetTeamMessages = () => {
  teamErrorMessage.value = ''
  teamSuccessMessage.value = ''
}

const resetRoleMessages = () => {
  roleErrorMessage.value = ''
  roleSuccessMessage.value = ''
}

const resetRoleForm = () => {
  editingRoleId.value = null
  roleForm.value = { name: '', code: '', description: '' }
}

const closeRoleModal = () => {
  isRoleModalOpen.value = false
  resetRoleForm()
  resetRoleMessages()
}

const openCreateRoleModal = () => {
  resetRoleForm()
  resetRoleMessages()
  roleModalKey.value += 1
  nextTick(() => {
    isRoleModalOpen.value = true
  })
}

const startEditingRole = (role: { id: number, name: string, code: string, description: string }) => {
  editingRoleId.value = role.id
  roleForm.value = {
    name: role.name,
    code: role.code,
    description: role.description,
  }
  resetRoleMessages()
  roleModalKey.value += 1
  nextTick(() => {
    isRoleModalOpen.value = true
  })
}

const submitRole = async () => {
  isRoleSubmitting.value = true
  resetRoleMessages()

  try {
    const payload = { ...roleForm.value }
    const role = editingRoleId.value
      ? await coreApi.updateRole(editingRoleId.value, payload)
      : await coreApi.createRole(payload)

    await refreshNuxtData('core-roles')
    roleSuccessMessage.value = editingRoleId.value
      ? `Роль ${role.name} обновлена.`
      : `Роль ${role.name} создана.`
    isRoleModalOpen.value = false
    resetRoleForm()
  }
  catch (error: any) {
    const apiError = error?.data || error?.response?._data
    if (apiError && typeof apiError === 'object') {
      const firstMessage = Object.values(apiError).flat().find(Boolean)
      roleErrorMessage.value = String(firstMessage)
    }
    else {
      roleErrorMessage.value = editingRoleId.value ? 'Не удалось обновить роль.' : 'Не удалось создать роль.'
    }
  }
  finally {
    isRoleSubmitting.value = false
  }
}

const resetTeamForm = () => {
  editingTeamId.value = null
  teamForm.value = { name: '', code: '', description: '' }
}

const closeTeamModal = () => {
  isTeamModalOpen.value = false
  resetTeamForm()
  resetTeamMessages()
}

const openCreateTeamModal = () => {
  resetTeamForm()
  resetTeamMessages()
  teamModalKey.value += 1
  nextTick(() => {
    isTeamModalOpen.value = true
  })
}

const startEditingTeam = (team: { id: number, name: string, code: string, description: string }) => {
  editingTeamId.value = team.id
  teamForm.value = {
    name: team.name,
    code: team.code,
    description: team.description,
  }
  resetTeamMessages()
  teamModalKey.value += 1
  nextTick(() => {
    isTeamModalOpen.value = true
  })
}

const submitTeam = async () => {
  isTeamSubmitting.value = true
  resetTeamMessages()

  try {
    const payload = { ...teamForm.value }
    const team = editingTeamId.value
      ? await coreApi.updateTeam(editingTeamId.value, payload)
      : await coreApi.createTeam(payload)

    await refreshTeams()
    await refreshNuxtData('core-teams')
    teamSuccessMessage.value = editingTeamId.value
      ? `Команда ${team.name} обновлена.`
      : `Команда ${team.name} создана.`
    isTeamModalOpen.value = false
    resetTeamForm()
  }
  catch (error: any) {
    const apiError = error?.data || error?.response?._data
    if (apiError && typeof apiError === 'object') {
      const firstMessage = Object.values(apiError).flat().find(Boolean)
      teamErrorMessage.value = String(firstMessage)
    }
    else {
      teamErrorMessage.value = editingTeamId.value ? 'Не удалось обновить команду.' : 'Не удалось создать команду.'
    }
  }
  finally {
    isTeamSubmitting.value = false
  }
}

const resetUserMessages = () => {
  userErrorMessage.value = ''
  userSuccessMessage.value = ''
}

const resetUserForm = () => {
  editingUserId.value = null
  userForm.value = {
    email: '',
    firstName: '',
    lastName: '',
    roleId: null,
    primaryTeamId: null,
    teamIds: [],
    isActive: true,
    isStaff: false,
    password: '',
  }
}

const closeUserModal = () => {
  isUserModalOpen.value = false
  resetUserForm()
  resetUserMessages()
}

const openCreateUserModal = () => {
  resetUserForm()
  resetUserMessages()
  userModalKey.value += 1
  nextTick(() => {
    isUserModalOpen.value = true
  })
}

const startEditingUser = (user: {
  id: number
  email: string
  firstName: string
  lastName: string
  role: string
  primaryTeam: string
  teams: number[]
  isActive: boolean
  isStaff: boolean
}) => {
  editingUserId.value = user.id
  userForm.value = {
    email: user.email,
    firstName: user.firstName,
    lastName: user.lastName,
    roleId: rolesOptions.value.find((role) => role.name === user.role)?.id || null,
    primaryTeamId: teamsOptions.value.find((team) => team.name === user.primaryTeam)?.id || null,
    teamIds: user.teams,
    isActive: user.isActive,
    isStaff: user.isStaff,
    password: '',
  }
  resetUserMessages()
  userModalKey.value += 1
  nextTick(() => {
    isUserModalOpen.value = true
  })
}

const submitUser = async () => {
  isUserSubmitting.value = true
  resetUserMessages()

  try {
    const payload = {
      email: userForm.value.email,
      first_name: userForm.value.firstName,
      last_name: userForm.value.lastName,
      role_id: userForm.value.roleId,
      primary_team_id: userForm.value.primaryTeamId,
      team_ids: userForm.value.teamIds,
      is_active: userForm.value.isActive,
      is_staff: userForm.value.isStaff,
      password: userForm.value.password,
    }
    const user = editingUserId.value
      ? await coreApi.updateUser(editingUserId.value, payload)
      : await coreApi.createUser(payload)

    await refreshUsers()
    await refreshNuxtData('core-users')
    userSuccessMessage.value = editingUserId.value
      ? `Пользователь ${user.email} обновлён.`
      : `Пользователь ${user.email} создан.`
    isUserModalOpen.value = false
    resetUserForm()
  }
  catch (error: any) {
    const apiError = error?.data || error?.response?._data
    if (apiError && typeof apiError === 'object') {
      const firstMessage = Object.values(apiError).flat().find(Boolean)
      userErrorMessage.value = String(firstMessage)
    }
    else {
      userErrorMessage.value = editingUserId.value ? 'Не удалось обновить пользователя.' : 'Не удалось создать пользователя.'
    }
  }
  finally {
    isUserSubmitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <section class="space-y-6">
      <div class="block-radius overflow-hidden border border-ink-200 bg-white shadow-sm">
        <div class="border-b border-ink-200 p-3">
          <nav class="grid grid-cols-5 gap-2">
            <button
              v-for="section in sections"
              :key="section.id"
              class="btn btn-sm w-full text-center text-xs"
              :class="activeSection === section.id ? 'border-sky-200 bg-sky-100 text-sky-700 shadow-sm hover:bg-sky-100' : 'btn-ghost'"
              @click="activeSection = section.id"
            >
              <span>{{ section.label }}</span>
            </button>
          </nav>
        </div>

        <div class="p-6">
          <div v-if="isQuarterSection" class="space-y-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-ink-900">Кварталы OKR</h2>
                <p class="mt-1 text-sm text-ink-500">Создание, редактирование и переключение активного периода.</p>
              </div>
              <button class="btn btn-primary" @click="openCreateQuarterModal">
                <Plus class="h-4 w-4" />
                Добавить квартал
              </button>
            </div>

            <div v-if="quarterSuccessMessage" class="block-radius border border-mint-500/20 bg-mint-100 px-4 py-3 text-sm text-mint-500">
              {{ quarterSuccessMessage }}
            </div>

            <div class="block-radius overflow-hidden border border-ink-200">
              <div v-if="quartersPending" class="bg-white px-4 py-6 text-sm text-ink-500">Загружаем кварталы...</div>
              <UiEmptyState v-else-if="!quarterOptions.length" class="m-4" title="Кварталы ещё не созданы" description="Создайте первый квартал через кнопку выше." />
              <div v-else class="overflow-x-auto">
                <table class="min-w-full bg-white text-sm">
                  <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
                    <tr>
                      <th class="px-4 py-3 font-medium">Название</th>
                      <th class="px-4 py-3 font-medium">Активный</th>
                      <th class="px-4 py-3 font-medium">Дата начала</th>
                      <th class="px-4 py-3 font-medium">Дата окончания</th>
                      <th class="px-4 py-3 font-medium">Действия</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-ink-100 text-ink-600">
                    <tr v-for="quarter in quarterOptions" :key="quarter.id" class="hover:bg-ink-50/60">
                      <td class="px-4 py-4 font-medium text-ink-900">{{ quarter.name }}</td>
                      <td class="px-4 py-4"><UiStatusBadge :status="quarter.isActive ? 'active' : 'draft'" size="sm" /></td>
                      <td class="px-4 py-4">{{ quarter.startDate }}</td>
                      <td class="px-4 py-4">{{ quarter.endDate }}</td>
                      <td class="px-4 py-4">
                        <button class="btn btn-secondary btn-sm" @click="startEditingQuarter(quarter)">
                          <Pencil class="h-4 w-4" />
                          Редактировать
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activeSection === 'roles'" class="space-y-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-ink-900">Роли</h2>
                <p class="mt-1 text-sm text-ink-500">Управление бизнес-ролями продукта.</p>
              </div>
              <button class="btn btn-primary" @click="openCreateRoleModal">
                <Plus class="h-4 w-4" />
                Добавить роль
              </button>
            </div>
            <div v-if="roleSuccessMessage" class="block-radius border border-mint-500/20 bg-mint-100 px-4 py-3 text-sm text-mint-500">
              {{ roleSuccessMessage }}
            </div>
            <div class="block-radius overflow-hidden border border-ink-200">
              <UiEmptyState v-if="!rolesOptions.length" class="m-4" title="Ролей пока нет" description="Добавьте первую роль через кнопку выше." />
              <div v-else class="overflow-x-auto">
                <table class="min-w-full bg-white text-sm">
                  <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
                    <tr>
                      <th class="px-4 py-3 font-medium">Название</th>
                      <th class="px-4 py-3 font-medium">Код</th>
                      <th class="px-4 py-3 font-medium">Описание</th>
                      <th class="px-4 py-3 font-medium">Действия</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-ink-100 text-ink-600">
                    <tr v-for="role in rolesOptions" :key="role.id" class="hover:bg-ink-50/60">
                      <td class="px-4 py-4 font-medium text-ink-900">{{ role.name }}</td>
                      <td class="px-4 py-4">{{ role.code }}</td>
                      <td class="px-4 py-4">{{ role.description || '—' }}</td>
                      <td class="px-4 py-4">
                        <button class="btn btn-secondary btn-sm" @click="startEditingRole(role)">
                          <Pencil class="h-4 w-4" />
                          Редактировать
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activeSection === 'users'" class="space-y-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-ink-900">Пользователи</h2>
                <p class="mt-1 text-sm text-ink-500">Управление пользователями, ролями и командами.</p>
              </div>
              <button class="btn btn-primary" @click="openCreateUserModal">
                <Plus class="h-4 w-4" />
                Добавить пользователя
              </button>
            </div>
            <div v-if="userSuccessMessage" class="block-radius border border-mint-500/20 bg-mint-100 px-4 py-3 text-sm text-mint-500">
              {{ userSuccessMessage }}
            </div>
            <div class="block-radius overflow-hidden border border-ink-200">
              <div v-if="usersPending" class="bg-white px-4 py-6 text-sm text-ink-500">Загружаем пользователей...</div>
              <UiEmptyState v-else-if="!usersOptions.length" class="m-4" title="Пользователей пока нет" description="Добавьте первого пользователя через кнопку выше." />
              <div v-else class="overflow-x-auto">
                <table class="min-w-full bg-white text-sm">
                  <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
                    <tr>
                      <th class="px-4 py-3 font-medium">Email</th>
                      <th class="px-4 py-3 font-medium">Имя</th>
                      <th class="px-4 py-3 font-medium">Роль</th>
                      <th class="px-4 py-3 font-medium">Основная команда</th>
                      <th class="px-4 py-3 font-medium">Активен</th>
                      <th class="px-4 py-3 font-medium">Действия</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-ink-100 text-ink-600">
                    <tr v-for="user in usersOptions" :key="user.id" class="hover:bg-ink-50/60">
                      <td class="px-4 py-4 font-medium text-ink-900">{{ user.email }}</td>
                      <td class="px-4 py-4">{{ [user.firstName, user.lastName].filter(Boolean).join(' ') || '—' }}</td>
                      <td class="px-4 py-4">{{ user.role || '—' }}</td>
                      <td class="px-4 py-4">{{ user.primaryTeam || '—' }}</td>
                      <td class="px-4 py-4"><UiStatusBadge :status="user.isActive ? 'active' : 'draft'" size="sm" /></td>
                      <td class="px-4 py-4">
                        <button class="btn btn-secondary btn-sm" @click="startEditingUser(user)">
                          <Pencil class="h-4 w-4" />
                          Редактировать
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activeSection === 'teams'" class="space-y-4">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-ink-900">Команды</h2>
                <p class="mt-1 text-sm text-ink-500">Управление инженерными и продуктовыми командами.</p>
              </div>
              <button class="btn btn-primary" @click="openCreateTeamModal">
                <Plus class="h-4 w-4" />
                Добавить команду
              </button>
            </div>
            <div v-if="teamSuccessMessage" class="block-radius border border-mint-500/20 bg-mint-100 px-4 py-3 text-sm text-mint-500">
              {{ teamSuccessMessage }}
            </div>
            <div class="block-radius overflow-hidden border border-ink-200">
              <div v-if="teamsPending" class="bg-white px-4 py-6 text-sm text-ink-500">Загружаем команды...</div>
              <UiEmptyState v-else-if="!teamsOptions.length" class="m-4" title="Команд пока нет" description="Добавьте первую команду через кнопку выше." />
              <div v-else class="overflow-x-auto">
                <table class="min-w-full bg-white text-sm">
                  <thead class="bg-ink-50 text-left text-xs uppercase tracking-[0.2em] text-ink-400">
                    <tr>
                      <th class="px-4 py-3 font-medium">Название</th>
                      <th class="px-4 py-3 font-medium">Код</th>
                      <th class="px-4 py-3 font-medium">Описание</th>
                      <th class="px-4 py-3 font-medium">Участники</th>
                      <th class="px-4 py-3 font-medium">Действия</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-ink-100 text-ink-600">
                    <tr v-for="team in teamsOptions" :key="team.id" class="hover:bg-ink-50/60">
                      <td class="px-4 py-4 font-medium text-ink-900">{{ team.name }}</td>
                      <td class="px-4 py-4">{{ team.code }}</td>
                      <td class="px-4 py-4">{{ team.description || '—' }}</td>
                      <td class="px-4 py-4">{{ team.membersCount }}</td>
                      <td class="px-4 py-4">
                        <button class="btn btn-secondary btn-sm" @click="startEditingTeam(team)">
                          <Pencil class="h-4 w-4" />
                          Редактировать
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else class="space-y-4">
            <div>
              <h2 class="text-lg font-semibold text-ink-900">Уведомления</h2>
              <p class="mt-1 text-sm text-ink-500">Раздел будет связан с backend после добавления системных настроек.</p>
            </div>
            <UiEmptyState title="Раздел в работе" description="Здесь появятся настройки напоминаний и digest-рассылок." />
          </div>
        </div>
      </div>
    </section>

    <div v-if="isQuarterModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/45 px-4 py-6" @click.self="closeQuarterModal">
      <div :key="quarterModalKey" class="surface w-full max-w-lg p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-lg font-semibold text-ink-900">{{ quarterFormTitle }}</p>
            <p class="mt-1 text-sm text-ink-500">{{ editingQuarterId ? 'Измените параметры выбранного периода.' : 'Новый период сразу появится в системе.' }}</p>
          </div>
          <button class="btn btn-secondary btn-icon" @click="closeQuarterModal" aria-label="Закрыть модалку"><X class="h-4 w-4" /></button>
        </div>
        <form :key="`${editingQuarterId ?? 'new'}-${quarterModalKey}`" class="mt-6 grid gap-4" @submit.prevent="submitQuarter">
          <label class="grid gap-2 text-sm text-ink-600"><span>Год</span><input v-model.number="quarterForm.year" type="number" min="2000" max="3000" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Квартал</span><select v-model.number="quarterForm.quarter" class="input-base"><option :value="1">Q1</option><option :value="2">Q2</option><option :value="3">Q3</option><option :value="4">Q4</option></select></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Дата начала</span><input v-model="quarterForm.startDate" type="date" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Дата окончания</span><input v-model="quarterForm.endDate" type="date" class="input-base"></label>
          <label class="block-radius flex items-center gap-3 border border-ink-200 px-4 py-3 text-sm text-ink-600"><input v-model="quarterForm.isActive" type="checkbox" class="h-4 w-4 rounded border-ink-300 text-sky-500 focus:ring-sky-500"><span>Сделать квартал активным</span></label>
          <div v-if="quarterErrorMessage" class="block-radius border border-rose-200 bg-rose-100 px-4 py-3 text-sm text-rose-500">{{ quarterErrorMessage }}</div>
          <div class="flex items-center justify-end gap-3 pt-2">
            <button type="button" class="btn btn-secondary" @click="closeQuarterModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="isQuarterSubmitting"><Save class="h-4 w-4" />{{ isQuarterSubmitting ? 'Сохраняем...' : quarterFormButtonLabel }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isTeamModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/45 px-4 py-6" @click.self="closeTeamModal">
      <div :key="teamModalKey" class="surface w-full max-w-lg p-6">
        <div class="flex items-start justify-between gap-4">
          <div><p class="text-lg font-semibold text-ink-900">{{ editingTeamId ? 'Редактировать команду' : 'Создать команду' }}</p></div>
          <button class="btn btn-secondary btn-icon" @click="closeTeamModal" aria-label="Закрыть модалку"><X class="h-4 w-4" /></button>
        </div>
        <form class="mt-6 grid gap-4" @submit.prevent="submitTeam">
          <label class="grid gap-2 text-sm text-ink-600"><span>Название</span><input v-model="teamForm.name" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Код</span><input v-model="teamForm.code" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Описание</span><textarea v-model="teamForm.description" class="input-base min-h-28" /></label>
          <div v-if="teamErrorMessage" class="block-radius border border-rose-200 bg-rose-100 px-4 py-3 text-sm text-rose-500">{{ teamErrorMessage }}</div>
          <div class="flex items-center justify-end gap-3 pt-2">
            <button type="button" class="btn btn-secondary" @click="closeTeamModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="isTeamSubmitting"><Save class="h-4 w-4" />{{ isTeamSubmitting ? 'Сохраняем...' : editingTeamId ? 'Сохранить изменения' : 'Добавить команду' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isRoleModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/45 px-4 py-6" @click.self="closeRoleModal">
      <div :key="roleModalKey" class="surface w-full max-w-lg p-6">
        <div class="flex items-start justify-between gap-4">
          <div><p class="text-lg font-semibold text-ink-900">{{ editingRoleId ? 'Редактировать роль' : 'Создать роль' }}</p></div>
          <button class="btn btn-secondary btn-icon" @click="closeRoleModal" aria-label="Закрыть модалку"><X class="h-4 w-4" /></button>
        </div>
        <form class="mt-6 grid gap-4" @submit.prevent="submitRole">
          <label class="grid gap-2 text-sm text-ink-600"><span>Название</span><input v-model="roleForm.name" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Код</span><input v-model="roleForm.code" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Описание</span><textarea v-model="roleForm.description" class="input-base min-h-28" /></label>
          <div v-if="roleErrorMessage" class="block-radius border border-rose-200 bg-rose-100 px-4 py-3 text-sm text-rose-500">{{ roleErrorMessage }}</div>
          <div class="flex items-center justify-end gap-3 pt-2">
            <button type="button" class="btn btn-secondary" @click="closeRoleModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="isRoleSubmitting"><Save class="h-4 w-4" />{{ isRoleSubmitting ? 'Сохраняем...' : editingRoleId ? 'Сохранить изменения' : 'Добавить роль' }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isUserModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/45 px-4 py-6" @click.self="closeUserModal">
      <div :key="userModalKey" class="surface w-full max-w-2xl p-6">
        <div class="flex items-start justify-between gap-4">
          <div><p class="text-lg font-semibold text-ink-900">{{ editingUserId ? 'Редактировать пользователя' : 'Создать пользователя' }}</p></div>
          <button class="btn btn-secondary btn-icon" @click="closeUserModal" aria-label="Закрыть модалку"><X class="h-4 w-4" /></button>
        </div>
        <form class="mt-6 grid gap-4 md:grid-cols-2" @submit.prevent="submitUser">
          <label class="grid gap-2 text-sm text-ink-600"><span>Email</span><input v-model="userForm.email" type="email" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Пароль</span><input v-model="userForm.password" type="password" class="input-base" :placeholder="editingUserId ? 'Оставьте пустым, чтобы не менять' : ''"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Имя</span><input v-model="userForm.firstName" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Фамилия</span><input v-model="userForm.lastName" class="input-base"></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Роль</span><select v-model.number="userForm.roleId" class="input-base"><option :value="null">Без роли</option><option v-for="role in rolesOptions" :key="role.id" :value="role.id">{{ role.name }}</option></select></label>
          <label class="grid gap-2 text-sm text-ink-600"><span>Основная команда</span><select v-model.number="userForm.primaryTeamId" class="input-base"><option :value="null">Без команды</option><option v-for="team in teamsOptions" :key="team.id" :value="team.id">{{ team.name }}</option></select></label>
          <label class="grid gap-2 text-sm text-ink-600 md:col-span-2">
            <span>Команды</span>
            <div class="block-radius border border-ink-200 bg-ink-50 p-3">
              <label v-for="team in teamsOptions" :key="team.id" class="flex items-center gap-3 py-1 text-sm text-ink-700">
                <input v-model="userForm.teamIds" type="checkbox" :value="team.id" class="h-4 w-4 rounded border-ink-300 text-sky-500 focus:ring-sky-500">
                <span>{{ team.name }}</span>
              </label>
            </div>
          </label>
          <label class="block-radius flex items-center gap-3 border border-ink-200 px-4 py-3 text-sm text-ink-600"><input v-model="userForm.isActive" type="checkbox" class="h-4 w-4 rounded border-ink-300 text-sky-500 focus:ring-sky-500"><span>Активен</span></label>
          <label class="block-radius flex items-center gap-3 border border-ink-200 px-4 py-3 text-sm text-ink-600"><input v-model="userForm.isStaff" type="checkbox" class="h-4 w-4 rounded border-ink-300 text-sky-500 focus:ring-sky-500"><span>Доступ в админку</span></label>
          <div v-if="userErrorMessage" class="block-radius border border-rose-200 bg-rose-100 px-4 py-3 text-sm text-rose-500 md:col-span-2">{{ userErrorMessage }}</div>
          <div class="flex items-center justify-end gap-3 pt-2 md:col-span-2">
            <button type="button" class="btn btn-secondary" @click="closeUserModal">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="isUserSubmitting"><Save class="h-4 w-4" />{{ isUserSubmitting ? 'Сохраняем...' : editingUserId ? 'Сохранить изменения' : 'Добавить пользователя' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
