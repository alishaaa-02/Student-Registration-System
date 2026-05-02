document.addEventListener("DOMContentLoaded", function(){

    // Fade in body
    document.body.style.opacity = "0";

    setTimeout(() => {
        document.body.style.transition = "1s";
        document.body.style.opacity = "1";
    }, 200);

    // Button click ripple effect
    const buttons = document.querySelectorAll(".btn, .nav-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function(){
            btn.style.transform = "scale(0.95)";
            setTimeout(()=>{
                btn.style.transform = "";
            },150);
        });
    });

});

function updateClock(){

    const clock = document.getElementById("liveClock");

    if(clock){

        const now = new Date();

        clock.innerHTML =
            now.toLocaleDateString() + " | " +
            now.toLocaleTimeString();
    }
}

setInterval(updateClock, 1000);
updateClock();

setTimeout(() => {

    const flash = document.querySelector(".flash-message");

    if(flash){
        flash.style.transition = "0.5s";
        flash.style.opacity = "0";

        setTimeout(()=>{
            flash.remove();
        },500);
    }

},3000);