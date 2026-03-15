export const useOkrLookups = async (cacheKeyPrefix: string) => {
  const okrApi = useOkrApi()
  const coreApi = useCoreApi()

  const [
    { data: users, pending: usersPending },
    { data: teams, pending: teamsPending },
    { data: quarters, pending: quartersPending },
  ] = await Promise.all([
    useAsyncData(`${cacheKeyPrefix}-users`, () => coreApi.fetchUsers(), {
      server: false,
      default: () => [],
    }),
    useAsyncData(`${cacheKeyPrefix}-teams`, () => coreApi.fetchTeams(), {
      server: false,
      default: () => [],
    }),
    useAsyncData(`${cacheKeyPrefix}-quarters`, () => okrApi.fetchQuarters(), {
      server: false,
      default: () => [],
    }),
  ])

  const isLoading = computed(() => usersPending.value || teamsPending.value || quartersPending.value)

  return {
    users,
    teams,
    quarters,
    isLoading,
  }
}
