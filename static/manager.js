document.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('.dirrection');
    const submitButton = document.querySelector('.submit');

    if (!selects.length || !submitButton) return;

    submitButton.addEventListener('click', async (e) => {
        e.preventDefault();
        const order = {};

        selects.forEach((select, index) => {
            order[index + 1] = select.value;
        });

        try {
            const response = await fetch('/update_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(order)
            });
            console.log("Порядок обновлен:", await response.json());
        } catch (error) {
            console.error("Ошибка:", error);
        }
    });
});