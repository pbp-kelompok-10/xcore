function showToast(title, message, type = "normal", duration = 3000) {
  const toast = document.getElementById("toast-component");
  const toastTitle = document.getElementById("toast-title");
  const toastMessage = document.getElementById("toast-message");

  if (!toast) return;

  // Fill in text
  toastTitle.textContent = title;
  toastMessage.textContent = message;

  // Reset color styles
  toast.style.borderColor = "#e5e7eb";
  toast.style.color = "#1f2937";

  // Type-specific border colors
  if (type === "success") toast.style.borderColor = "#22c55e";
  else if (type === "error") toast.style.borderColor = "#ef4444";
  else if (type === "info") toast.style.borderColor = "#3b82f6";

  // Show toast
  toast.classList.add("show");

  // Hide after duration
  setTimeout(() => {
    toast.classList.remove("show");
  }, duration);
}
