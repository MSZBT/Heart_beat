document.addEventListener('DOMContentLoaded', () => {
    const submitButtonNames = document.querySelector('.submit_names');
    const indikator = document.querySelector('.indikator');
    const formsFetchs = document.querySelectorAll('.forms form');

    let formDataNames;

    function setupSubmitButtons() {
        const submitButtons = document.querySelectorAll('.submit');
        
        submitButtons.forEach(function(submitButton) {
            submitButton.addEventListener('click', async (e) => {
                e.preventDefault();
                submitButtons.forEach(function(btn) {
                    btn.classList.remove('active');
                });

                e.target.classList.add('active');

                let selects = e.target.parentElement.querySelectorAll('.dirrection');
                
                const order = {};

                selects.forEach((select, index) => {
                    order[index + 1] = select.value;
                });

                console.log(order);
                
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
    }

    setupSubmitButtons();

    submitButtonNames.addEventListener('click', function(event) {
        event.preventDefault(); 
        formDataNames = {
            "1": document.getElementById('athlete1').value,
            "2": document.getElementById('athlete2').value,
            "3": document.getElementById('athlete3').value,
            "4": document.getElementById('athlete4').value,
            "5": document.getElementById('athlete5').value,
            "6": document.getElementById('athlete6').value
        };
        indikator.innerHTML = '';
        let inputIndikator = '';
        for (let i = 0; i < 6; i++) {
            let newPart = `${i} -> ${formDataNames[(i + 1).toString()]}<br>` 
            inputIndikator += newPart;
        }
        indikator.innerHTML = inputIndikator;

        let count = 1;        
        formsFetchs.forEach(function(form) {
            form.innerHTML = "";
            let strFormFetch = `<label for="select">${count} этап</label><br>`;
            count += 1;
            for (let i = 0; i < 6; i++) {
                strFormFetch += `
                    <select class="dirrection" name="${i + 1}">
                    <option value="0" selected>0</option>
                    <option value="1">1 - ${formDataNames["1"]}</option>
                    <option value="2">2 - ${formDataNames["2"]}</option>
                    <option value="3">3 - ${formDataNames["3"]}</option>
                    <option value="4">4 - ${formDataNames["4"]}</option>
                    <option value="5">5 - ${formDataNames["5"]}</option>
                    <option value="6">6 - ${formDataNames["6"]}</option>
                </select>`;
            }

            strFormFetch +='<button class="submit">Submit</button>';

            form.innerHTML = strFormFetch;
        });
        setupSubmitButtons();
    });
});