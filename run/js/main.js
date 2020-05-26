var form = document.getElementById('sendImg')
var preloader = document.querySelector('.preloader')
const url = "http://localhost:5000/test"



form.addEventListener('submit',(e)=>{
    preloader.style['display'] = 'block';
    e.preventDefault()
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url); 

    xhr.responseType = 'blob';
    xhr.onload = function(event){ 
        var blob = new Blob([this.response.value,{type: 'audio/wav'}])
        const aurl = window.URL.createObjectURL(this.response);
        console.log(aurl);
        window.audio = new Audio();
        window.audio.src = aurl;
        preloader.style['display'] = 'none';
        Materialize.toast('Playing Audio', 3000, 'rounded');
        window.audio.play();   
    }; 
    // or onerror, onabort
    var formData = new FormData(form); 
    
    xhr.send(formData);
    console.log(formData.getAll('lang'));
    
})
