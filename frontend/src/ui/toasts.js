import { ref } from "vue";

export const toasts = ref([]);

let toastSeq = 0;

export function showToast({ message, retry = null }) {
  const exists = toasts.value.some((toast) => toast.message === message);
  if (exists) {
    return;
  }

  const id = ++toastSeq;
  toasts.value.push({ id, message, retry });

  if (!retry) {
    window.setTimeout(() => dismissToast(id), 5000);
  }
}

export function dismissToast(id) {
  toasts.value = toasts.value.filter((toast) => toast.id !== id);
}
