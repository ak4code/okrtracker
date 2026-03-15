type OkrStatus =
  | 'draft'
  | 'on track'
  | 'at risk'
  | 'completed'

interface CheckIn {
  id: string
  author: string
  date: string
  value: number
  note: string
}

interface KeyResult {
  id: string
  title: string
  owner: string
  current: number
  target: number
  unit: string
  status: OkrStatus
  lastCheckIn: string
  history: CheckIn[]
}

interface OkrItem {
  id: string
  title: string
  description: string
  owner: string
  ownerRole: string
  team: string
  quarter: string
  status: OkrStatus
  progress: number
  priority: 'Low' | 'Medium' | 'High'
  risks: string[]
  initiatives: string[]
  keyResults: KeyResult[]
  comments: number
  updatedAt: string
}

const currentQuarter = 'Q2 2026'

const okrs: OkrItem[] = [
  {
    id: 'ENG-Q2-01',
    title: 'Сократить lead time релизов платформы',
    description: 'Ускорить выпуск фич без роста инцидентов и ручной координации между командами.',
    owner: 'Анна Смирнова',
    ownerRole: 'Engineering Manager',
    team: 'Platform',
    quarter: 'Q2 2026',
    status: 'at risk',
    progress: 0.3,
    priority: 'High',
    risks: ['Нестабильность пайплайна на staging', 'Не закрыта автоматизация rollback'],
    initiatives: ['Release train v2', 'Canary rollout policy'],
    comments: 7,
    updatedAt: '2026-03-11',
    keyResults: [
      {
        id: 'KR-101',
        title: 'Снизить средний lead time с 5.4 до 2.5 дней',
        owner: 'Илья Ветров',
        current: 3.1,
        target: 2.5,
        unit: 'days',
        status: 'at risk',
        lastCheckIn: '2026-03-12',
        history: [
          { id: 'c1', author: 'Илья Ветров', date: '2026-03-12', value: 3.1, note: 'Стабилизировали сборки after merge.' },
          { id: 'c2', author: 'Илья Ветров', date: '2026-03-05', value: 3.6, note: 'Добавили параллельные e2e джобы.' },
        ],
      },
      {
        id: 'KR-102',
        title: 'Довести долю автодеплоев в production до 85%',
        owner: 'Мария Коваль',
        current: 71,
        target: 85,
        unit: '%',
        status: 'on track',
        lastCheckIn: '2026-03-10',
        history: [
          { id: 'c3', author: 'Мария Коваль', date: '2026-03-10', value: 71, note: 'Перевели billing и notifications на единый flow.' },
          { id: 'c4', author: 'Мария Коваль', date: '2026-03-03', value: 63, note: 'Подготовили шаблон релизных гардов.' },
        ],
      },
    ],
  },
  {
    id: 'ENG-Q2-02',
    title: 'Поднять предсказуемость delivery для продуктовой команды',
    description: 'Сделать выполнение квартальных целей прозрачным для product и engineering.',
    owner: 'Дмитрий Орлов',
    ownerRole: 'Team Lead',
    team: 'Frontend',
    quarter: 'Q2 2026',
    status: 'on track',
    progress: 0.9,
    priority: 'Medium',
    risks: ['Не все команды ведут еженедельный check-in'],
    initiatives: ['Weekly review cadence', 'Definition of done v3'],
    comments: 4,
    updatedAt: '2026-03-12',
    keyResults: [
      {
        id: 'KR-201',
        title: 'Снизить долю просроченных задач из квартального scope до 10%',
        owner: 'Дмитрий Орлов',
        current: 14,
        target: 10,
        unit: '%',
        status: 'on track',
        lastCheckIn: '2026-03-12',
        history: [
          { id: 'c5', author: 'Дмитрий Орлов', date: '2026-03-12', value: 14, note: 'Вывели критические блокеры в отдельный weekly review.' },
        ],
      },
      {
        id: 'KR-202',
        title: 'Поддерживать факт weekly check-in не ниже 95%',
        owner: 'Виктория Сергеева',
        current: 96,
        target: 95,
        unit: '%',
        status: 'completed',
        lastCheckIn: '2026-03-11',
        history: [
          { id: 'c6', author: 'Виктория Сергеева', date: '2026-03-11', value: 96, note: 'Команда работает в новой cadence третью неделю подряд.' },
        ],
      },
    ],
  },
  {
    id: 'ENG-Q2-03',
    title: 'Снизить дефекты после релиза в критических сценариях',
    description: 'Усилить качество проверок и предрелизные сигналы для QA и backend-команд.',
    owner: 'Екатерина Новикова',
    ownerRole: 'QA Lead',
    team: 'Quality',
    quarter: 'Q2 2026',
    status: 'at risk',
    progress: 0.3,
    priority: 'High',
    risks: ['Недостаточно покрытия smoke для legacy checkout', 'Не внедрены mutation checks'],
    initiatives: ['Critical path coverage', 'Bug burn-down'],
    comments: 11,
    updatedAt: '2026-03-09',
    keyResults: [
      {
        id: 'KR-301',
        title: 'Снизить post-release critical bugs c 9 до 3 за квартал',
        owner: 'Екатерина Новикова',
        current: 7,
        target: 3,
        unit: 'bugs',
        status: 'at risk',
        lastCheckIn: '2026-03-09',
        history: [
          { id: 'c7', author: 'Екатерина Новикова', date: '2026-03-09', value: 7, note: 'Checkout все еще основной источник регрессий.' },
        ],
      },
      {
        id: 'KR-302',
        title: 'Довести автопокрытие smoke-критериев до 90%',
        owner: 'Олег Федин',
        current: 62,
        target: 90,
        unit: '%',
        status: 'at risk',
        lastCheckIn: '2026-03-08',
        history: [
          { id: 'c8', author: 'Олег Федин', date: '2026-03-08', value: 62, note: 'Собрали missing scenarios по платежам.' },
        ],
      },
    ],
  },
  {
    id: 'ENG-Q2-04',
    title: 'Улучшить onboarding новых инженеров',
    description: 'Сократить время до первого продуктивного вклада и сделать адаптацию предсказуемой.',
    owner: 'Ирина Лебедева',
    ownerRole: 'People Partner',
    team: 'Operations',
    quarter: 'Q2 2026',
    status: 'on track',
    progress: 0.7,
    priority: 'Medium',
    risks: [],
    initiatives: ['Engineering onboarding map', 'Buddy checklist'],
    comments: 3,
    updatedAt: '2026-03-07',
    keyResults: [
      {
        id: 'KR-401',
        title: 'Сократить time-to-first-PR с 10 до 5 рабочих дней',
        owner: 'Ирина Лебедева',
        current: 6.5,
        target: 5,
        unit: 'days',
        status: 'on track',
        lastCheckIn: '2026-03-07',
        history: [
          { id: 'c9', author: 'Ирина Лебедева', date: '2026-03-07', value: 6.5, note: 'Новый onboarding backlog уже у 4 сотрудников.' },
        ],
      },
    ],
  },
  {
    id: 'ENG-Q3-01',
    title: 'Подготовить platform baseline для Q3 roadmap',
    description: 'Собрать техническую базу под инициативы следующего квартала и снизить риски старта.',
    owner: 'Анна Смирнова',
    ownerRole: 'Engineering Manager',
    team: 'Platform',
    quarter: 'Q3 2026',
    status: 'draft',
    progress: 0.3,
    priority: 'High',
    risks: ['Зависимость от новой observability stack'],
    initiatives: ['Platform roadmap prep', 'SLO review'],
    comments: 2,
    updatedAt: '2026-03-13',
    keyResults: [
      {
        id: 'KR-501',
        title: 'Сформировать и согласовать baseline инициатив до конца квартала',
        owner: 'Анна Смирнова',
        current: 1,
        target: 4,
        unit: 'items',
        status: 'draft',
        lastCheckIn: '2026-03-13',
        history: [
          { id: 'c10', author: 'Анна Смирнова', date: '2026-03-13', value: 1, note: 'Собрали первый draft roadmap на Q3.' },
        ],
      },
    ],
  },
  {
    id: 'ENG-Q3-02',
    title: 'Подготовить команду Frontend к redesign analytics',
    description: 'Выделить цели следующего квартала под новый аналитический контур и стабильную delivery cadence.',
    owner: 'Дмитрий Орлов',
    ownerRole: 'Team Lead',
    team: 'Frontend',
    quarter: 'Q3 2026',
    status: 'draft',
    progress: 0.3,
    priority: 'Medium',
    risks: [],
    initiatives: ['Analytics redesign kickoff'],
    comments: 1,
    updatedAt: '2026-03-13',
    keyResults: [
      {
        id: 'KR-601',
        title: 'Собрать список ключевых KR для Q3',
        owner: 'Дмитрий Орлов',
        current: 1,
        target: 5,
        unit: 'KR',
        status: 'draft',
        lastCheckIn: '2026-03-13',
        history: [
          { id: 'c11', author: 'Дмитрий Орлов', date: '2026-03-13', value: 1, note: 'Есть первая версия инициативы по analytics redesign.' },
        ],
      },
    ],
  },
]

const users = [
  { name: 'Анна Смирнова', role: 'Руководитель', team: 'Platform', status: 'Active', access: 'Несколько команд' },
  { name: 'Дмитрий Орлов', role: 'Тимлид', team: 'Frontend', status: 'Active', access: 'Команда' },
  { name: 'Екатерина Новикова', role: 'Сотрудник', team: 'Quality', status: 'Pending invite', access: 'Свои OKR' },
  { name: 'Ирина Лебедева', role: 'Администратор', team: 'Operations', status: 'Active', access: 'Админ-разделы' },
]

const teams = [
  { name: 'Platform', progress: 0.5, atRisk: 1, overdue: 2 },
  { name: 'Frontend', progress: 0.9, atRisk: 0, overdue: 1 },
  { name: 'Quality', progress: 0.3, atRisk: 2, overdue: 3 },
  { name: 'Operations', progress: 0.7, atRisk: 0, overdue: 0 },
]

export const useMockData = () => {
  const quarters = [...new Set(okrs.map((okr) => okr.quarter))]
  const currentQuarterOkrs = okrs.filter((okr) => okr.quarter === currentQuarter)
  const nextQuarter = quarters.find((quarter) => quarter !== currentQuarter)

  const totalKeyResults = okrs.reduce((sum, okr) => sum + okr.keyResults.length, 0)
  const completedKeyResults = okrs.reduce(
    (sum, okr) => sum + okr.keyResults.filter((kr) => kr.status === 'completed').length,
    0,
  )

  const stats = [
    { label: 'Командные OKR', value: String(currentQuarterOkrs.length).padStart(2, '0'), hint: `Все команды · ${currentQuarter}`, tone: 'sky' },
    { label: 'Средний прогресс', value: '0.6', hint: `Средний агрегат по текущему кварталу`, tone: 'mint' },
    { label: 'Просроченные check-in', value: '06', hint: 'Нужно обновить сегодня', tone: 'amber' },
    { label: 'Проблемные OKR', value: '03', hint: 'Статус at risk', tone: 'rose' },
  ]

  const upcomingCheckIns = [
    { title: 'Release train v2', owner: 'Илья Ветров', due: 'Сегодня, 17:00', status: 'at risk' as OkrStatus },
    { title: 'Checkout smoke coverage', owner: 'Олег Федин', due: '14 марта', status: 'at risk' as OkrStatus },
    { title: 'Weekly delivery review', owner: 'Виктория Сергеева', due: '15 марта', status: 'on track' as OkrStatus },
  ]

  return {
    okrs,
    quarters,
    currentQuarter,
    nextQuarter,
    currentQuarterOkrs,
    users,
    teams,
    stats,
    upcomingCheckIns,
    totalKeyResults,
    completedKeyResults,
  }
}
