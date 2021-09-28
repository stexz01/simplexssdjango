const start = document.getElementById('startSearch')
start.addEventListener('click', ()=>{
    let spinner = document.getElementById('redSpinner')
    spinner.innerHTML = `<div class="spinner-border text-danger" style="width: 3rem; height: 3rem;" role="status"></div>`
})