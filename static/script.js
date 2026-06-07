async function sendCommand(command){

console.log("Sending:", command);

const res = await fetch('/buzzer', {
method:'POST',

headers:{
'Content-Type':'application/json'
},

body:JSON.stringify({
command: command
})

});

const result =
await res.json();

console.log(result);

document.getElementById(
'log-content'
).innerText +=
`\n> Buzzer: ${command}`;

}