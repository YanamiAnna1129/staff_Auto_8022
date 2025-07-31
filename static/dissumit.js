function disableSubmit(form) {
    const btn = form.querySelector('input[type="submit"]');
    btn.disabled = true;
    btn.value = "正在登入...";
}