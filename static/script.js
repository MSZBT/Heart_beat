/*let owners;
let oldDirrection = {};
async function fetchHeartRate() {
    try {
        const response_dirrection = await fetch("/get_order");
        if (!response_dirrection.ok) throw new Error("Network error");
        const dirrection_data = await response_dirrection.json();
        console.log(dirrection_data); // объект место - устройство

        const response = await fetch("/get_heart_rate");
        if (!response.ok) throw new Error("Network error");
        const data = await response.json();
        if (!data) return;

        titrs = document.querySelector(".titrs");
        
        if (JSON.stringify(oldDirrection) !== JSON.stringify(dirrection_data)) {
            titrs.innerHTML = "";
            for (const [k, v] of Object.entries(dirrection_data)) {  
                titrs.innerHTML += `
                <div class="ownerBlock" name="${v}">
                    <div class="testHeart"></div>
                    <p></p>
                </div>`;
            }
            oldDirrection = dirrection_data; 
        }

        owners = document.querySelectorAll(".ownerBlock"); 

        owners.forEach((owner, index) => {
            let adress = owner.attributes('name');

            if (index + 1 === adress) {
                const text = owner.querySelector("p");
                const heart = owner.querySelector(".testHeart");
                const heartRate = data[index + 1] || data[index]; 

                if (text) {
                    if (heartRate && heartRate !== "N/D" && heartRate !== "0") {
                        text.textContent = heartRate;
                        heart.style.backgroundColor = "red";
                    } else {
                        text.textContent = "";
                        heart.style.backgroundColor = "grey";
                    }
                }
            }
        });
    } catch (error) {
        console.error("Fetch error:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    owners = document.querySelectorAll(".ownerBlock"); 
    setInterval(fetchHeartRate, 1000);
    fetchHeartRate();
});*/

let owners;
let oldDirrection = {};
async function fetchHeartRate() {
    try {
        const response_dirrection = await fetch("/get_order");
        if (!response_dirrection.ok) throw new Error("Network error");
        const dirrection_data = await response_dirrection.json();
        console.log("Назначение устройств:", dirrection_data);

        const response = await fetch("/get_heart_rate");
        if (!response.ok) throw new Error("Network error");
        const data = await response.json();
        console.log("Данные пульса:", data);
        if (!data) return;

        const titrs = document.querySelector(".titrs");
        
        if (JSON.stringify(oldDirrection) !== JSON.stringify(dirrection_data)) {
            titrs.innerHTML = "";
            for (const [position, deviceId] of Object.entries(dirrection_data)) {  
                titrs.innerHTML += `
                <div class="ownerBlock" name="${deviceId}" data-position="${position}">
                    <div class="testHeart"></div>
                    <p></p>
                </div>`;
            }
            oldDirrection = {...dirrection_data};
        }

        owners = document.querySelectorAll(".ownerBlock"); 

        owners.forEach((owner) => {
            const deviceId = owner.getAttribute('name'); 
            const position = owner.getAttribute('data-position'); 
            const text = owner.querySelector("p");
            const heart = owner.querySelector(".testHeart");
            
            // Получаем данные пульса для этого устройства
            const heartRate = data[deviceId] || 'N/D';

            if (text) {
                if (heartRate && heartRate !== "N/D" && heartRate !== "0") {
                    text.textContent = `${heartRate}`;
                    heart.style.backgroundColor = "red";
                } else {
                    text.textContent = "";
                    heart.style.backgroundColor = "grey";
                }
            }
        });
    } catch (error) {
        console.error("Fetch error:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setInterval(fetchHeartRate, 1000);
    fetchHeartRate();
});