let owners;

async function fetchHeartRate() {
    try {
        const response_dirrection = await fetch("/get_order");
        if (!response_dirrection.ok) throw new Error("Network error");
        const dirrection_data = await response_dirrection.json();
        console.log(dirrection_data);

        const response = await fetch("/get_heart_rate");
        if (!response.ok) throw new Error("Network error");
        const data = await response.json();
        if (!data) return;

        owners = document.querySelectorAll(".ownerBlock"); 
        
        owners.forEach((owner, index) => {
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
        });
    } catch (error) {
        console.error("Fetch error:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    owners = document.querySelectorAll(".ownerBlock"); 
    setInterval(fetchHeartRate, 1000);
    fetchHeartRate();
});

