    var form = document.getElementById('sendImg')
    
const url = "http://localhost:5000/test"
console.log("????")


form.addEventListener('submit',(e)=>{
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
        window.audio.play();   
    }; 
    // or onerror, onabort
    var formData = new FormData(form); 
    
    xhr.send(formData);
    console.log(formData.getAll('lang'));
    
})
