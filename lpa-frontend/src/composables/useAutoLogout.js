import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

export function useAutoLogout(timeoutMinutes = 30) {
  const router = useRouter()
  const userStore = useUserStore()
  const timeoutId = ref(null)
  
  // Timeout v milisekundách
  const TIMEOUT_MS = timeoutMinutes * 60 * 1000

  function resetTimer() {
    // Vyčistit starý timer
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }

    // Nastavit nový timer
    timeoutId.value = setTimeout(() => {
      handleLogout()
    }, TIMEOUT_MS)
  }

  function handleLogout() {
    userStore.logout()
    router.push('/')
    alert('Byli jste odhlášeni z důvodu neaktivity')
  }

  function setupActivityListeners() {
    // Události, které resetují timer
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    events.forEach(event => {
      document.addEventListener(event, resetTimer, true)
    })

    // Iniciální spuštění
    resetTimer()
  }

  function removeActivityListeners() {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    events.forEach(event => {
      document.removeEventListener(event, resetTimer, true)
    })

    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }
  }

  onMounted(() => {
    setupActivityListeners()
  })

  onUnmounted(() => {
    removeActivityListeners()
  })

  return {
    resetTimer,
    handleLogout
  }
}
